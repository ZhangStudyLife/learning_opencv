from pathlib import Path

import cv2

SCRIPT_DIR = Path(__file__).resolve().parent
IMAGE_PATH = SCRIPT_DIR.parent / "images" / "opencv_logo.jpg"

# 读取图片，创建一个名为 "Loaded Image" 的窗口，显示该图片。
image = cv2.imread(str(IMAGE_PATH))

# imshow() 的第一个参数是窗口名称，第二个参数是要显示的图像。
cv2.imshow("Loaded Image", image)

# 显示蓝色通道、绿色通道和红色通道的图像。
cv2.imshow("blue",image[:,:,0])
cv2.imshow("green",image[:,:,1])
cv2.imshow("red",image[:,:,2])

# 将图像转换为灰度图像。
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
cv2.imshow("grey",gray)

# 等待用户按下任意键后关闭所有窗口。
cv2.waitKey(0)
cv2.destroyAllWindows()
