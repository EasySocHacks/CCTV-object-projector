import random
from typing import List

from detector.common_detector import CommonDetector
from detector.implementation import Detectron2Detector


class DetectorPool:
    def __init__(self, size: int, device, detector_type=Detectron2Detector):
        self.size = size
        self.detector_type = detector_type
        self.device = device

        self.pool: List[CommonDetector] = []
        for pool_id in range(size):
            self.pool.append(detector_type(device))

    def detect(self, image, detector_number=None):
        if detector_number is None:
            return self.pool[random.randint(0, self.size - 1)].detect(image)
        else:
            return self.pool[detector_number].detect(image)

    def decode_class(self, class_id: int):
        return self.detector_type.decode_class(class_id)
