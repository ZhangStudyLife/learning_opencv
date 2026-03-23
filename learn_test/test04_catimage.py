from pathlib import Path

import cv2

SCRIPT_DIR = Path(__file__).resolve().parent
IMAGE_PATH = SCRIPT_DIR.parent / "images" / "opencv_logo.jpg"

image = cv2.imread(str(IMAGE_PATH))

# 先横向裁剪，再纵向裁剪
# 先横向0:100，再纵向0:200
corp = image[0:100, 0:200]
cv2.imshow("corp", corp)
cv2.waitKey(0)
