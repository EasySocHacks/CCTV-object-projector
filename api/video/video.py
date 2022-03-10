from abc import ABC

import cv2


class Video(ABC):
    def __init__(self, path, video_id, camera):
        self.path = path
        self.video_id = video_id
        self.camera = camera

        self.video_capture = cv2.VideoCapture(path)
