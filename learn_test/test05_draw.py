import cv2
import numpy as np

# 创建一个300x300的黑色图像
image = np.zeros([300,300,3],np.uint8)
# 在图像上绘制一个绿色矩形
cv2.rectangle(image,(50,50),(250,250),(0,255,0),-1)
# 在图像上绘制一个蓝色圆形
cv2.circle(image,(150,150),50,(255,0,0),-1)
# 在图像上绘制一条红色直线
cv2.line(image,(0,0),(300,300),(0,0,255),5)
# 在图像上绘制一个白色的文本
font = cv2.FONT_HERSHEY_SIMPLEX
cv2.putText(image,'OpenCV',(100,100),font,2,(255,255,255),2,cv2.LINE_AA)
# 显示图像
cv2.imshow("Drawings",image)
cv2.waitKey(0)
cv2.destroyAllWindows()