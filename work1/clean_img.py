from pathlib import Path

import cv2

SCRIPT_DIR = Path(__file__).resolve().parent
IMAGE_PATH = SCRIPT_DIR.parent / "images" / "Piano_Sheet_Music.png"
OUTPUT_PATH = SCRIPT_DIR.parent / "images" / "Piano_Sheet_Music_clean.png"

image = cv2.imread(str(IMAGE_PATH), cv2.IMREAD_GRAYSCALE)
if image is None:
    raise FileNotFoundError(f"无法读取图片: {IMAGE_PATH}")

# 1) 先放大，提升观感清晰度
upscaled = cv2.resize(image, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_LANCZOS4)

# 2) 轻度去噪，避免锐化时把噪点一起放大
denoised = cv2.fastNlMeansDenoising(upscaled, None, h=10, templateWindowSize=7, searchWindowSize=21)

# 3) 局部对比度增强，让音符和五线谱更明显
clahe = cv2.createCLAHE(clipLimit=3.5, tileGridSize=(8, 8))
contrast = clahe.apply(denoised)

# 4) 更强锐化
blur = cv2.GaussianBlur(contrast, (0, 0), 1.2)
sharpened = cv2.addWeighted(contrast, 2.2, blur, -1.2, 0)

# 5) 再做一次轻微拉伸，让黑更黑、白更白
result = cv2.normalize(sharpened, None, 0, 255, cv2.NORM_MINMAX)

cv2.imwrite(str(OUTPUT_PATH), result)

print(f"已保存增强图: {OUTPUT_PATH}")

# 预览
cv2.imshow("original", image)
cv2.imshow("clean", result)
cv2.waitKey(0)
cv2.destroyAllWindows()
