import time
from typing import Union, Callable

import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtMultimedia import QCameraDevice, QMediaDevices
from PyQt6.QtWidgets import QWidget, QLabel
from cv2 import VideoCapture

from .pose_estimation import PoseEstimator
from .pyquantum.ui import Column, ComboBox, Row, Spacer, Button
from .pyquantum.value import Value


pose_estimator = PoseEstimator()

class CameraDeviceComboBox(ComboBox):
    def __init__(
            self,
            parent: QWidget,
            enabled: Union[Value, bool] = True,
            camera_device_changed: Callable[[QCameraDevice, int], None] = None,
    ):
        self.camera_devices = QMediaDevices.videoInputs()

        def index_changed(index: int):
            if camera_device_changed is not None:
                camera_device_changed(self.camera_devices[index], index)

        super(CameraDeviceComboBox, self).__init__(
            parent=parent,
            items=[cam.description() for cam in self.camera_devices],
            enabled=enabled,
            index_changed=index_changed,
        )

    def current_camera_device(self) -> QCameraDevice:
        return self.camera_devices[self.currentIndex()]


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    latency_signal = pyqtSignal(int)

    def __init__(self, index: int, midi_callback: Callable):
        super().__init__()
        self.index = index
        self._run_flag = True
        self.midi_callback = midi_callback
        self.preview = True

    def run(self):
        # capture from web cam
        self._run_flag = True
        cap = VideoCapture(self.index)
        t1 = time.time()
        while self._run_flag:
            ret, img = cap.read()
            if ret:
                keypoints, deltas = pose_estimator(cv2.resize(img[:, :, ::-1], (192, 192)))
                t2 = time.time()
                d = int((t2 - t1) * 1000)

                deltas = {k: v / d for k, v in deltas.items()}
                self.latency_signal.emit(int(deltas["RightHandSpeed"] * 10000))
                t1 = t2
                self.midi_callback(**keypoints)
                if self.preview:
                    img = self.draw_keypoints(img, keypoints)
                    self.change_pixmap_signal.emit(img)


        cap.release()

    def draw_keypoints(self, image: np.ndarray, kp: dict) -> np.ndarray:
        h, w, c = image.shape
        def draw_keypoint(image, x, y, color):
            return cv2.circle(
                image,
                (int((1 - x) * w), int((1- y) * h)),
                radius=10,
                color=color,
                thickness=-1,
            )

        image = draw_keypoint(image, kp['NoseX'], kp['NoseY'], color=(255, 0, 0))
        image = draw_keypoint(image, kp['LeftHandX'], kp['LeftHandY'], color=(0, 255, 0))
        image = draw_keypoint(image, kp['RightHandX'], kp['RightHandY'], color=(0, 0, 255))
        return image

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()


class VideoWidget(QLabel):
    def __init__(self, parent: QWidget):
        super(VideoWidget, self).__init__(parent=parent)
        self._stretch = 0
        self.size = (640, 480)
        self.set_image(np.zeros((480, 640, 3), dtype=np.uint8))

    def set_image(self, image: np.ndarray):
        image = cv2.cvtColor(image[:, ::-1], cv2.COLOR_BGR2RGB)
        h, w, ch = image.shape
        bytes_per_line = ch * w

        convert_to_Qt_format = QImage(image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        p = convert_to_Qt_format.scaled(*self.size, Qt.AspectRatioMode.KeepAspectRatio)
        self.setPixmap(QPixmap.fromImage(p))


def void(*args, **kwargs):
    return

class CameraUI(QWidget):
    def __init__(self, parent: QWidget, midi_callback = void):
        super(CameraUI, self).__init__(parent=parent)
        self.capturing = Value(False)
        self.preview = Value(True)

        self.camera_combo_box = CameraDeviceComboBox(
            parent=self,
            camera_device_changed=self.set_camera,
        )

        self.latency_label = QLabel(self)

        def update_latency(value: int):
            self.latency_label.setText(f"Latency: {value:.4f} ms")

        update_latency(0)

        self.video_widget = VideoWidget(self)
        self.video_thread = VideoThread(self.camera_combo_box.currentIndex(), midi_callback)
        self.video_thread.change_pixmap_signal.connect(self.video_widget.set_image)
        self.video_thread.latency_signal.connect(update_latency)

        self.setLayout(Column(
            children=[
                self.camera_combo_box,
                self.video_widget,
                self.latency_label,
                Row([
                    Button(
                        parent=self,
                        value=self.preview.map(lambda c: "Disable Preview" if c else "Enable Preview"),
                        on_click=self.toggle_preview,
                    ),
                    Spacer(1),
                    Button(
                        parent=self,
                        value=self.capturing.map(lambda c: "Stop" if c else "Start"),
                        on_click=self.toggle_start_stop,
                    )
                ])
            ],
            stretch=0
        ))

    def toggle_preview(self):
        if self.preview.data:
            self.video_thread.preview = False
            self.preview.set_data(False)
        else:
            self.video_thread.preview = True
            self.preview.set_data(True)

    def toggle_start_stop(self):
        if self.capturing.data:
            self.video_thread.stop()
            self.capturing.set_data(False)
        else:
            self.video_thread.start()
            self.capturing.set_data(True)

    def set_camera(self, device: QCameraDevice, index: int):
        if self.capturing.data:
            self.video_thread.stop()
            self.video_thread.index = index
            self.video_thread.start()
        else:
            self.video_thread.index = index