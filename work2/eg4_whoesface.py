from pathlib import Path

import cv2

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
IMAGE_PATH = PROJECT_DIR / "images" / "boy.png"
CASCADE_PATH = Path("/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml")

face_cascade = cv2.CascadeClassifier(str(CASCADE_PATH))
if face_cascade.empty():
    raise FileNotFoundError(f"无法加载人脸分类器: {CASCADE_PATH}")

image = cv2.imread(str(IMAGE_PATH))
if image is None:
    raise FileNotFoundError(f"无法读取图片: {IMAGE_PATH}")

gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
faces = face_cascade.detectMultiScale(
    gray_image,
    scaleFactor=1.1,
    minNeighbors=5,
    minSize=(30, 30),
)

print(f"检测到 {len(faces)} 张人脸")

for (x, y, w, h) in faces:
    cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)

cv2.imshow("Detected Faces", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
