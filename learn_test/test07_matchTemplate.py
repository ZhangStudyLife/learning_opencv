from pathlib import Path

import cv2

SCRIPT_DIR = Path(__file__).resolve().parent
IMAGE_PATH = SCRIPT_DIR.parent / "images" / "opencv_logo.jpg"

image = cv2.imread(str(IMAGE_PATH))
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Harris角点检测
# 计算Harris角点，参数：blockSize、ksize、k
# blockSize: 用于角点检测的邻域大小，必须是正的奇数。blockSize 越大，检测到的角点越少，但更可靠。
# ksize: Sobel 算子的大小，必须是正的奇数。用于计算图像梯度。
# k Harris 检测器的阈值，表示角点响应函数中数据点的权重。取值范围通常在 0.04 到 0.06 之间。
# borderType: 像素外推方法。默认为 BORDER_DEFAULT。


# corners：输出图像，与输入图像 src 大小相同，类型为 CV_8UC1（8位单通道）。图像中的每一个像素值表示该位置成为角点的可能性，值越大表示可能性越高。
corner = cv2.cornerHarris(gray, 2, 3, 0.04)
# 膨胀，突出角点，扩大角点区域
corner = cv2.dilate(corner, None)

# 设定阈值，标记角点
image[corner > 0.01 * corner.max()] = [0, 0, 255]
cv2.imshow("corner", image)

# 显示原图像和角点检测结果
cv2.waitKey(0)
cv2.destroyAllWindows()
