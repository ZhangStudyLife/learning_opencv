import base64
from pathlib import Path
import math
import time
import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox, ttk
from typing import Optional

import cv2
import numpy as np


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_IMAGE_PATH = SCRIPT_DIR.parent / "images" / "girl.png"
MAX_PREVIEW_SIZE = (1280, 860)


def odd_at_least_three(value: int) -> int:
    value = max(3, int(value))
    return value if value % 2 == 1 else value + 1


def ensure_image(path: Path) -> np.ndarray:
    image = cv2.imread(str(path))
    if image is None:
        raise FileNotFoundError(f"无法读取图片: {path}")
    return image


def apply_mean(image: np.ndarray, params: dict) -> np.ndarray:
    ksize = odd_at_least_three(params["kernel"])
    return cv2.blur(image, (ksize, ksize))


def apply_gaussian(image: np.ndarray, params: dict) -> np.ndarray:
    ksize = odd_at_least_three(params["kernel"])
    sigma = max(0, params["gaussian_sigma"])
    return cv2.GaussianBlur(image, (ksize, ksize), sigma)


def apply_median(image: np.ndarray, params: dict) -> np.ndarray:
    ksize = odd_at_least_three(params["kernel"])
    return cv2.medianBlur(image, ksize)


def apply_bilateral(image: np.ndarray, params: dict) -> np.ndarray:
    diameter = max(3, int(params["bilateral_d"]))
    return cv2.bilateralFilter(
        image,
        diameter,
        max(1, params["bilateral_sigma_color"]),
        max(1, params["bilateral_sigma_space"]),
    )


def apply_box(image: np.ndarray, params: dict) -> np.ndarray:
    ksize = odd_at_least_three(params["kernel"])
    return cv2.boxFilter(image, -1, (ksize, ksize), normalize=True)


def apply_nlm(image: np.ndarray, params: dict) -> np.ndarray:
    return cv2.fastNlMeansDenoisingColored(
        image,
        None,
        max(1, params["nlm_h"]),
        max(1, params["nlm_h_color"]),
        7,
        21,
    )


ALGORITHMS = [
    ("mean", "均值滤波", apply_mean),
    ("gaussian", "高斯滤波", apply_gaussian),
    ("median", "中值滤波", apply_median),
    ("bilateral", "双边滤波", apply_bilateral),
    ("box", "方框滤波", apply_box),
    ("nlm", "非局部均值去噪", apply_nlm),
]

PREVIEW_TITLES = {
    "原图": "Original",
    "均值滤波": "Mean Blur",
    "高斯滤波": "Gaussian Blur",
    "中值滤波": "Median Blur",
    "双边滤波": "Bilateral Filter",
    "方框滤波": "Box Filter",
    "非局部均值去噪": "Non-Local Means",
}

PREFERRED_CJK_FONTS = [
    "Noto Sans CJK SC",
    "Noto Sans SC",
    "Source Han Sans SC",
    "WenQuanYi Zen Hei",
    "WenQuanYi Micro Hei",
    "Microsoft YaHei",
    "SimHei",
    "PingFang SC",
    "Heiti SC",
    "AR PL UKai CN",
    "AR PL UMing CN",
]


def pick_cjk_font(root: tk.Tk) -> Optional[str]:
    available = set(tkfont.families(root))
    for family in PREFERRED_CJK_FONTS:
        if family in available:
            return family
    return None


def configure_ui_fonts(root: tk.Tk) -> None:
    family = pick_cjk_font(root)
    if not family:
        return

    for font_name, size in [
        ("TkDefaultFont", 10),
        ("TkTextFont", 10),
        ("TkMenuFont", 10),
        ("TkHeadingFont", 10),
        ("TkCaptionFont", 10),
    ]:
        font = tkfont.nametofont(font_name)
        font.configure(family=family, size=size)


def to_preview_title(title: str) -> str:
    name, sep, suffix = title.partition(" (")
    preview_name = PREVIEW_TITLES.get(name, name)
    return preview_name if not sep else f"{preview_name} ({suffix}"


class BlurComparisonApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("模糊算法对比")
        self.root.geometry("1460x920")
        self.root.minsize(1100, 760)

        self.current_image_path = DEFAULT_IMAGE_PATH
        self.original_image = ensure_image(self.current_image_path)
        self.preview_photo = None
        self.current_collage = None

        self.algorithm_vars = {
            "mean": tk.BooleanVar(value=True),
            "gaussian": tk.BooleanVar(value=True),
            "median": tk.BooleanVar(value=True),
            "bilateral": tk.BooleanVar(value=True),
            "box": tk.BooleanVar(value=False),
            "nlm": tk.BooleanVar(value=False),
        }

        self.kernel_var = tk.IntVar(value=5)
        self.gaussian_sigma_var = tk.IntVar(value=0)
        self.bilateral_d_var = tk.IntVar(value=9)
        self.bilateral_sigma_color_var = tk.IntVar(value=75)
        self.bilateral_sigma_space_var = tk.IntVar(value=75)
        self.nlm_h_var = tk.IntVar(value=10)
        self.nlm_h_color_var = tk.IntVar(value=10)
        self.status_var = tk.StringVar()
        self.metrics_var = tk.StringVar(value="耗时信息将在这里显示")

        self._build_layout()
        self._refresh_preview()

    def _build_layout(self) -> None:
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        control_frame = ttk.Frame(self.root, padding=14)
        control_frame.grid(row=0, column=0, sticky="ns")

        preview_frame = ttk.Frame(self.root, padding=(0, 14, 14, 14))
        preview_frame.grid(row=0, column=1, sticky="nsew")
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)

        ttk.Label(control_frame, text="图片路径").grid(row=0, column=0, sticky="w")
        self.path_label = ttk.Label(
            control_frame,
            text=str(self.current_image_path),
            wraplength=320,
            foreground="#444444",
        )
        self.path_label.grid(row=1, column=0, sticky="w", pady=(2, 8))

        ttk.Button(control_frame, text="选择图片", command=self._choose_image).grid(
            row=2, column=0, sticky="ew", pady=(0, 12)
        )

        ttk.Label(control_frame, text="选择对比算法").grid(row=3, column=0, sticky="w")
        algo_frame = ttk.Frame(control_frame)
        algo_frame.grid(row=4, column=0, sticky="ew", pady=(6, 12))
        for index, (key, label, _) in enumerate(ALGORITHMS):
            ttk.Checkbutton(
                algo_frame,
                text=label,
                variable=self.algorithm_vars[key],
                command=self._refresh_preview,
            ).grid(row=index, column=0, sticky="w", pady=1)

        params_frame = ttk.LabelFrame(control_frame, text="参数设置", padding=10)
        params_frame.grid(row=5, column=0, sticky="ew")
        params_frame.columnconfigure(0, weight=1)

        self._add_scale(
            params_frame,
            "基础核大小",
            self.kernel_var,
            3,
            31,
            0,
            "均值 / 高斯 / 中值 / 方框滤波共用",
        )
        self._add_scale(
            params_frame,
            "高斯 sigma",
            self.gaussian_sigma_var,
            0,
            20,
            2,
            "0 表示由 OpenCV 自动估计",
        )
        self._add_scale(
            params_frame,
            "双边直径",
            self.bilateral_d_var,
            3,
            21,
            4,
            "双边滤波邻域大小",
        )
        self._add_scale(
            params_frame,
            "双边颜色 sigma",
            self.bilateral_sigma_color_var,
            10,
            150,
            6,
            "值越大越平滑",
        )
        self._add_scale(
            params_frame,
            "双边空间 sigma",
            self.bilateral_sigma_space_var,
            10,
            150,
            8,
            "控制空间距离影响",
        )
        self._add_scale(
            params_frame,
            "NLM 强度 h",
            self.nlm_h_var,
            1,
            25,
            10,
            "非局部均值亮度通道强度",
        )
        self._add_scale(
            params_frame,
            "NLM 颜色 h",
            self.nlm_h_color_var,
            1,
            25,
            12,
            "非局部均值颜色通道强度",
        )

        ttk.Button(control_frame, text="刷新结果", command=self._refresh_preview).grid(
            row=6, column=0, sticky="ew", pady=(12, 6)
        )
        ttk.Button(control_frame, text="保存当前对比图", command=self._save_collage).grid(
            row=7, column=0, sticky="ew", pady=(0, 6)
        )
        ttk.Button(control_frame, text="恢复默认", command=self._reset_defaults).grid(
            row=8, column=0, sticky="ew"
        )

        metrics_frame = ttk.LabelFrame(control_frame, text="处理耗时", padding=10)
        metrics_frame.grid(row=9, column=0, sticky="ew", pady=(12, 0))
        ttk.Label(
            metrics_frame,
            textvariable=self.metrics_var,
            justify="left",
            wraplength=320,
            foreground="#444444",
        ).grid(row=0, column=0, sticky="w")

        self.preview_label = ttk.Label(preview_frame, anchor="center")
        self.preview_label.grid(row=0, column=0, sticky="nsew")

        status_label = ttk.Label(
            preview_frame,
            textvariable=self.status_var,
            anchor="w",
            foreground="#555555",
        )
        status_label.grid(row=1, column=0, sticky="ew", pady=(10, 0))

    def _add_scale(
        self,
        parent: ttk.Frame,
        label: str,
        variable: tk.IntVar,
        min_value: int,
        max_value: int,
        row: int,
        hint: str,
    ) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w")
        ttk.Scale(
            parent,
            from_=min_value,
            to=max_value,
            orient="horizontal",
            variable=variable,
            command=lambda _value: self._refresh_preview(),
        ).grid(row=row + 1, column=0, sticky="ew")
        value_label = ttk.Label(parent, textvariable=variable)
        value_label.grid(row=row + 1, column=1, sticky="w", padx=(8, 0))
        ttk.Label(parent, text=hint, foreground="#666666", wraplength=300).grid(
            row=row + 2, column=0, columnspan=2, sticky="w", pady=(0, 8)
        )

    def _choose_image(self) -> None:
        file_path = filedialog.askopenfilename(
            title="选择要比较的图片",
            filetypes=[
                ("Image Files", "*.png *.jpg *.jpeg *.bmp *.webp"),
                ("All Files", "*.*"),
            ],
        )
        if not file_path:
            return

        try:
            self.current_image_path = Path(file_path)
            self.original_image = ensure_image(self.current_image_path)
            self.path_label.config(text=str(self.current_image_path))
            self._refresh_preview()
        except FileNotFoundError as exc:
            messagebox.showerror("读取失败", str(exc))

    def _reset_defaults(self) -> None:
        self.algorithm_vars["mean"].set(True)
        self.algorithm_vars["gaussian"].set(True)
        self.algorithm_vars["median"].set(True)
        self.algorithm_vars["bilateral"].set(True)
        self.algorithm_vars["box"].set(False)
        self.algorithm_vars["nlm"].set(False)

        self.kernel_var.set(5)
        self.gaussian_sigma_var.set(0)
        self.bilateral_d_var.set(9)
        self.bilateral_sigma_color_var.set(75)
        self.bilateral_sigma_space_var.set(75)
        self.nlm_h_var.set(10)
        self.nlm_h_color_var.set(10)
        self._refresh_preview()

    def _save_collage(self) -> None:
        if self.current_collage is None:
            messagebox.showwarning("无法保存", "当前还没有可保存的对比图。")
            return

        default_name = f"{self.current_image_path.stem}_blur_compare.png"
        file_path = filedialog.asksaveasfilename(
            title="保存当前对比图",
            initialfile=default_name,
            defaultextension=".png",
            filetypes=[
                ("PNG Image", "*.png"),
                ("JPEG Image", "*.jpg"),
                ("All Files", "*.*"),
            ],
        )
        if not file_path:
            return

        if cv2.imwrite(file_path, self.current_collage):
            self.status_var.set(f"已保存对比图: {Path(file_path).name}")
        else:
            messagebox.showerror("保存失败", "图片写入失败，请检查目标路径。")

    def _collect_params(self) -> dict:
        return {
            "kernel": odd_at_least_three(self.kernel_var.get()),
            "gaussian_sigma": self.gaussian_sigma_var.get(),
            "bilateral_d": self.bilateral_d_var.get(),
            "bilateral_sigma_color": self.bilateral_sigma_color_var.get(),
            "bilateral_sigma_space": self.bilateral_sigma_space_var.get(),
            "nlm_h": self.nlm_h_var.get(),
            "nlm_h_color": self.nlm_h_color_var.get(),
        }

    def _selected_algorithms(self):
        selected = []
        for key, label, func in ALGORITHMS:
            if self.algorithm_vars[key].get():
                selected.append((label, func))
        return selected

    def _refresh_preview(self) -> None:
        try:
            tiles = [("原图", self.original_image)]
            params = self._collect_params()
            timing_lines = ["原图: 0.00 ms"]
            total_ms = 0.0

            for label, func in self._selected_algorithms():
                start = time.perf_counter()
                output = func(self.original_image, params)
                elapsed_ms = (time.perf_counter() - start) * 1000
                total_ms += elapsed_ms
                tiles.append((f"{label} ({elapsed_ms:.2f} ms)", output))
                timing_lines.append(f"{label}: {elapsed_ms:.2f} ms")

            collage = self._build_collage(tiles)
            self.current_collage = collage
            display = self._resize_for_preview(collage)
            rgb_display = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
            success, encoded = cv2.imencode(".png", rgb_display)
            if not success:
                raise RuntimeError("预览图编码失败")
            self.preview_photo = tk.PhotoImage(
                data=base64.b64encode(encoded.tobytes()).decode("ascii")
            )
            self.preview_label.configure(image=self.preview_photo)
            self.metrics_var.set("\n".join(timing_lines))

            self.status_var.set(
                f"当前图片: {self.current_image_path.name} | 显示 {len(tiles)} 个结果 | 总处理耗时 {total_ms:.2f} ms"
            )
        except Exception as exc:  # pragma: no cover - GUI fallback
            self.current_collage = None
            self.status_var.set(f"处理失败: {exc}")

    def _build_collage(self, tiles):
        base_h, base_w = self.original_image.shape[:2]
        tile_w = 420
        tile_h = max(260, int(base_h * tile_w / base_w))
        gap = 18
        header_h = 36
        columns = 2 if len(tiles) <= 4 else 3
        rows = math.ceil(len(tiles) / columns)

        canvas_h = rows * (tile_h + header_h + gap) + gap
        canvas_w = columns * (tile_w + gap) + gap
        canvas = np.full((canvas_h, canvas_w, 3), 245, dtype=np.uint8)

        for index, (title, image) in enumerate(tiles):
            row = index // columns
            col = index % columns
            x = gap + col * (tile_w + gap)
            y = gap + row * (tile_h + header_h + gap)

            resized = cv2.resize(image, (tile_w, tile_h), interpolation=cv2.INTER_AREA)
            canvas[y + header_h : y + header_h + tile_h, x : x + tile_w] = resized
            cv2.rectangle(
                canvas,
                (x - 1, y + header_h - 1),
                (x + tile_w, y + header_h + tile_h),
                (160, 160, 160),
                1,
            )
            cv2.putText(
                canvas,
                to_preview_title(title),
                (x, y + 24),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.72,
                (40, 40, 40),
                2,
                cv2.LINE_AA,
            )

        return canvas

    def _resize_for_preview(self, image: np.ndarray) -> np.ndarray:
        max_w, max_h = MAX_PREVIEW_SIZE
        h, w = image.shape[:2]
        scale = min(max_w / w, max_h / h, 1.0)
        if scale == 1.0:
            return image
        new_size = (int(w * scale), int(h * scale))
        return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)


def main() -> None:
    root = tk.Tk()
    configure_ui_fonts(root)
    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")
    BlurComparisonApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
