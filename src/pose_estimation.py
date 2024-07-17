import numpy as np
import tensorflow as tf


class PoseEstimator:
    def __init__(self):
        self.interpreter = tf.lite.Interpreter(model_path="4.tflite")
        self.interpreter.allocate_tensors()
        self.last_keypoints = None

    def __call__(self, image: np.ndarray):
        self.interpreter.set_tensor(0, image[None, ])
        self.interpreter.invoke()
        keypoints = self.interpreter.get_tensor(332)[0, 0, :, :2]  # [17 2]
        if self.last_keypoints is not None:
            deltas = keypoints - self.last_keypoints
            self.last_keypoints = keypoints
        else:
            deltas = np.zeros_like(keypoints)
            self.last_keypoints = keypoints

        deltas = np.linalg.norm(deltas, axis=1)

        return self.keypoints_to_dict(keypoints), self.deltas_to_dict(deltas)

    def deltas_to_dict(self, deltas: np.ndarray) -> dict:
        return dict(
            NoseSpeed=deltas[0],
            LeftHandSpeed=deltas[9],
            RightHandSpeed=deltas[10]
        )


    def keypoints_to_dict(self, keypoints: np.ndarray) -> dict:
        keypoints = 1 - keypoints
        return dict(
            NoseX=keypoints[0, 1],
            NoseY=keypoints[0, 0],
            LeftHandX=keypoints[9, 1],
            LeftHandY=keypoints[9, 0],
            RightHandX=keypoints[10, 1],
            RightHandY=keypoints[10, 0],
        )