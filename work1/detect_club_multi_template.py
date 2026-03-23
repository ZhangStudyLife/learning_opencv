import argparse
import math
from dataclasses import dataclass
from pathlib import Path
from typing import List

import cv2
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DEFAULT_TEMPLATE_DIR = SCRIPT_DIR / "club_templates"
DEFAULT_RESULT_DIR = SCRIPT_DIR / "result"


def resolve_default_image_path():
    preferred = PROJECT_ROOT / "images" / "test_poker2.jpg"
    fallback = PROJECT_ROOT / "images" / "test_poker.jpg"
    return preferred if preferred.exists() else fallback


DEFAULT_IMAGE_PATH = resolve_default_image_path()


@dataclass
class Detection:
    x: int
    y: int
    w: int
    h: int
    match_score: float
    shape_score: float
    template_name: str

    @property
    def confidence(self):
        return 0.7 * self.match_score + 0.3 * self.shape_score

    @property
    def x2(self):
        return self.x + self.w

    @property
    def y2(self):
        return self.y + self.h

    @property
    def center(self):
        return (self.x + self.w / 2.0, self.y + self.h / 2.0)


@dataclass
class DetectionCluster:
    detections: List[Detection]

    @property
    def best(self):
        return max(self.detections, key=lambda item: item.confidence)

    @property
    def template_support(self):
        return len({item.template_name for item in self.detections})


def parse_args():
    parser = argparse.ArgumentParser(
        description="Detect club symbols using multiple template matches."
    )
    parser.add_argument(
        "--image",
        type=Path,
        default=DEFAULT_IMAGE_PATH,
        help=f"Input image path (default: {DEFAULT_IMAGE_PATH})",
    )
    parser.add_argument(
        "--templates",
        type=Path,
        default=DEFAULT_TEMPLATE_DIR,
        help=f"Template directory (default: {DEFAULT_TEMPLATE_DIR})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_RESULT_DIR,
        help=f"Result directory (default: {DEFAULT_RESULT_DIR})",
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.80,
        help="Minimum confidence for a final detection (default: 0.80)",
    )
    return parser.parse_args()


def load_color_image(path):
    image = cv2.imread(str(path))
    if image is None:
        raise FileNotFoundError(f"Cannot read input image: {path}")
    return image


def load_template_paths(template_dir):
    if not template_dir.exists():
        raise FileNotFoundError(f"Template directory does not exist: {template_dir}")

    suffixes = {".png", ".jpg", ".jpeg", ".bmp"}
    template_paths = [
        path
        for path in sorted(template_dir.iterdir())
        if path.is_file() and path.suffix.lower() in suffixes
    ]
    if not template_paths:
        raise FileNotFoundError(f"No template images found in: {template_dir}")
    return template_paths


def preprocess_gray(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.GaussianBlur(gray, (3, 3), 0)


def build_edge_map(gray_image):
    return cv2.Canny(gray_image, 50, 150)


def build_binary_mask(gray_image):
    blurred = cv2.GaussianBlur(gray_image, (3, 3), 0)
    _, mask = cv2.threshold(
        blurred,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
    )
    kernel = np.ones((3, 3), np.uint8)
    return cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)


def trim_foreground(gray_image, padding=2):
    mask = build_binary_mask(gray_image)
    ys, xs = np.where(mask > 0)
    if len(xs) == 0 or len(ys) == 0:
        return gray_image

    x1 = max(0, int(xs.min()) - padding)
    y1 = max(0, int(ys.min()) - padding)
    x2 = min(gray_image.shape[1], int(xs.max()) + padding + 1)
    y2 = min(gray_image.shape[0], int(ys.max()) + padding + 1)
    trimmed = gray_image[y1:y2, x1:x2]
    return trimmed if trimmed.size else gray_image


def compute_mask_iou(first_mask, second_mask):
    first = first_mask > 0
    second = second_mask > 0
    intersection = np.logical_and(first, second).sum()
    union = np.logical_or(first, second).sum()
    return float(intersection / union) if union else 0.0


def compute_box_iou(first, second):
    x1 = max(first.x, second.x)
    y1 = max(first.y, second.y)
    x2 = min(first.x2, second.x2)
    y2 = min(first.y2, second.y2)

    inter_w = max(0, x2 - x1)
    inter_h = max(0, y2 - y1)
    intersection = inter_w * inter_h
    if intersection == 0:
        return 0.0

    union = first.w * first.h + second.w * second.h - intersection
    return intersection / union if union else 0.0


def keep_by_nms(detections, iou_threshold):
    kept = []
    for detection in sorted(detections, key=lambda item: item.confidence, reverse=True):
        if all(compute_box_iou(detection, saved) <= iou_threshold for saved in kept):
            kept.append(detection)
    return kept


def match_single_template(source_gray, source_edges, template_path):
    template = cv2.imread(str(template_path), cv2.IMREAD_GRAYSCALE)
    if template is None:
        raise FileNotFoundError(f"Cannot read template image: {template_path}")

    template = trim_foreground(template)
    template_gray = cv2.GaussianBlur(template, (3, 3), 0)
    template_mask = build_binary_mask(template_gray)

    if (
        template_gray.shape[0] > source_gray.shape[0]
        or template_gray.shape[1] > source_gray.shape[1]
    ):
        return []

    gray_result = cv2.matchTemplate(
        source_gray,
        template_gray,
        cv2.TM_CCOEFF_NORMED,
    )

    template_edges = build_edge_map(template_gray)
    if np.count_nonzero(template_edges) > 0:
        edge_result = cv2.matchTemplate(
            source_edges,
            template_edges,
            cv2.TM_CCOEFF_NORMED,
        )
        combined_result = 0.75 * gray_result + 0.25 * edge_result
    else:
        combined_result = gray_result

    max_score = float(combined_result.max()) if combined_result.size else 0.0
    if max_score < 0.55:
        return []

    threshold = max(0.60, max_score - 0.40)
    ys, xs = np.where(combined_result >= threshold)

    detections = []
    template_h, template_w = template_gray.shape[:2]
    for y, x in zip(ys, xs):
        patch = source_gray[y : y + template_h, x : x + template_w]
        if patch.shape != template_gray.shape:
            continue

        patch_mask = build_binary_mask(patch)
        shape_score = compute_mask_iou(template_mask, patch_mask)
        if shape_score < 0.52:
            continue

        detections.append(
            Detection(
                x=int(x),
                y=int(y),
                w=int(template_w),
                h=int(template_h),
                match_score=float(combined_result[y, x]),
                shape_score=shape_score,
                template_name=template_path.name,
            )
        )

    return keep_by_nms(detections, iou_threshold=0.20)


def belongs_to_same_object(first, second):
    if compute_box_iou(first, second) >= 0.08:
        return True

    first_cx, first_cy = first.center
    second_cx, second_cy = second.center
    distance = math.hypot(first_cx - second_cx, first_cy - second_cy)
    max_size = max(first.w, first.h, second.w, second.h)
    width_ratio = min(first.w, second.w) / max(first.w, second.w)
    height_ratio = min(first.h, second.h) / max(first.h, second.h)

    return (
        width_ratio >= 0.40
        and height_ratio >= 0.40
        and distance <= max(12.0, 0.80 * max_size)
    )


def cluster_detections(detections):
    clusters = []
    for detection in sorted(detections, key=lambda item: item.confidence, reverse=True):
        for cluster in clusters:
            if any(belongs_to_same_object(detection, saved) for saved in cluster.detections):
                cluster.detections.append(detection)
                break
        else:
            clusters.append(DetectionCluster([detection]))
    return clusters


def filter_clusters(clusters, min_confidence):
    accepted = []
    for cluster in clusters:
        best = cluster.best
        if best.match_score < 0.60:
            continue
        if best.shape_score < 0.52:
            continue
        if best.confidence < min_confidence:
            continue
        accepted.append(cluster)
    return accepted


def deduplicate_clusters(clusters):
    kept = []
    ordered = sorted(
        clusters,
        key=lambda cluster: (cluster.best.confidence, cluster.template_support),
        reverse=True,
    )
    for cluster in ordered:
        if all(
            not belongs_to_same_object(cluster.best, saved.best)
            for saved in kept
        ):
            kept.append(cluster)
    return kept


def draw_results(source_image, clusters):
    result = source_image.copy()
    for cluster in clusters:
        best = cluster.best
        cv2.rectangle(
            result,
            (best.x, best.y),
            (best.x2, best.y2),
            (0, 255, 0),
            2,
        )

    label = f"clubs: {len(clusters)}"
    cv2.putText(
        result,
        label,
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (0, 255, 0),
        2,
        cv2.LINE_AA,
    )
    return result


def main():
    args = parse_args()
    image_path = args.image.resolve()
    template_dir = args.templates.resolve()
    output_dir = args.output_dir.resolve()

    source_image = load_color_image(image_path)
    template_paths = load_template_paths(template_dir)

    source_gray = preprocess_gray(source_image)
    source_edges = build_edge_map(source_gray)

    all_detections = []
    for template_path in template_paths:
        matches = match_single_template(source_gray, source_edges, template_path)
        print(f"{template_path.name}: {len(matches)} candidate(s)")
        all_detections.extend(matches)

    clusters = cluster_detections(all_detections)
    filtered_clusters = filter_clusters(clusters, min_confidence=args.min_confidence)
    final_clusters = deduplicate_clusters(filtered_clusters)

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{image_path.stem}_clubs_detected.png"
    result_image = draw_results(source_image, final_clusters)

    ok = cv2.imwrite(str(output_path), result_image)
    if not ok:
        raise OSError(f"Failed to save result image: {output_path}")

    print(f"Detected clubs: {len(final_clusters)}")
    for index, cluster in enumerate(final_clusters, start=1):
        best = cluster.best
        print(
            f"club_{index:02d}: "
            f"confidence={best.confidence:.3f}, "
            f"match={best.match_score:.3f}, "
            f"shape={best.shape_score:.3f}, "
            f"box=({best.x}, {best.y}, {best.w}, {best.h})"
        )
    print(f"Result image saved to: {output_path}")


if __name__ == "__main__":
    main()
