from pathlib import Path

import cv2

SCRIPT_DIR = Path(__file__).resolve().parent
IMAGE_PATH = SCRIPT_DIR.parent / "images" / "who.png"

# 读取图像
image = cv2.imread(str(IMAGE_PATH))

# 显示图像
cv2.imshow('Image Window', image)

# 等待用户按键
cv2.waitKey(0)

# 关闭所有窗口
cv2.destroyAllWindows()
