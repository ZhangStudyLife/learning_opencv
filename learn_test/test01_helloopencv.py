try:
    import cv2
    print(cv2.__version__)
    print("Hello OpenCV")
except Exception as e:
    print("An error occurred:", e)