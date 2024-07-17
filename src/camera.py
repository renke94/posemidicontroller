from cv2 import VideoCapture


class Camera:
    def __init__(self, index: int):
        self.device = VideoCapture(index=index)

    def release(self):
        self.device.release()

    def __del__(self):
        self.release()
