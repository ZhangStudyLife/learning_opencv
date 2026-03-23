import argparse
import shutil
from pathlib import Path

import cv2
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DEFAULT_TEMPLATE_DIR = SCRIPT_DIR / "club_templates"


def resolve_default_image_path():
    preferred = PROJECT_ROOT / "images" / "test_poker2.jpg"
    fallback = PROJECT_ROOT / "images" / "test_poker.jpg"
    return preferred if preferred.exists() else fallback


DEFAULT_IMAGE_PATH = resolve_default_image_path()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Manually select club templates from an image."
    )
    parser.add_argument(
        "--image",
        type=Path,
        default=DEFAULT_IMAGE_PATH,
        help=f"Input image path (default: {DEFAULT_IMAGE_PATH})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_TEMPLATE_DIR,
        help=f"Template output directory (default: {DEFAULT_TEMPLATE_DIR})",
    )
    return parser.parse_args()


def reset_directory(path):
    path.mkdir(parents=True, exist_ok=True)
    for child in path.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()


def load_image(path):
    image = cv2.imread(str(path))
    if image is None:
        raise FileNotFoundError(f"Cannot read input image: {path}")
    return image


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


def trim_foreground(color_image, padding=2):
    gray = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
    mask = build_binary_mask(gray)
    ys, xs = np.where(mask > 0)
    if len(xs) == 0 or len(ys) == 0:
        return color_image

    x1 = max(0, int(xs.min()) - padding)
    y1 = max(0, int(ys.min()) - padding)
    x2 = min(color_image.shape[1], int(xs.max()) + padding + 1)
    y2 = min(color_image.shape[0], int(ys.max()) + padding + 1)
    trimmed = color_image[y1:y2, x1:x2]
    return trimmed if trimmed.size else color_image


def save_templates(image, rois, output_dir):
    saved_paths = []
    for roi in rois:
        x, y, w, h = [int(value) for value in roi]
        if w <= 0 or h <= 0:
            continue

        crop = image[y : y + h, x : x + w]
        if crop.size == 0:
            continue
        crop = trim_foreground(crop)

        output_path = output_dir / f"club_template_{len(saved_paths) + 1:02d}.png"
        ok = cv2.imwrite(str(output_path), crop)
        if not ok:
            raise OSError(f"Failed to save template: {output_path}")
        saved_paths.append(output_path)

    return saved_paths


def main():
    args = parse_args()
    image_path = args.image.resolve()
    output_dir = args.output_dir.resolve()

    image = load_image(image_path)
    reset_directory(output_dir)

    print("Drag with the mouse to select a club region.")
    print("Press Enter or Space to confirm the current ROI.")
    print("Press Esc after the last ROI to finish and save.")

    rois = cv2.selectROIs(
        "Select club templates",
        image,
        showCrosshair=True,
        fromCenter=False,
    )
    cv2.destroyAllWindows()

    saved_paths = save_templates(image, rois, output_dir)
    if not saved_paths:
        print(f"No templates were selected. Directory left empty: {output_dir}")
        return

    print(f"Saved {len(saved_paths)} template(s) to: {output_dir}")
    for path in saved_paths:
        print(path)


if __name__ == "__main__":
    main()
