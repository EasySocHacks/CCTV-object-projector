import random
from typing import List

from detector.common_detector import CommonDetector


class DetectorPool:
    def __init__(self, size: int, detector_type):
        self.size = size
        self.detector_type = detector_type

        self.pool: List[CommonDetector] = []
        for pool_id in range(size):
            self.pool.append(detector_type())

    def detect(self, image, detector_id=None):
        if detector_id is None:
            return self.pool[random.randint(0, self.size - 1)].detect(image)
        else:
            return self.pool[detector_id].detect(image)

    def decode_class(self, class_id: int):
        return self.detector_type.decode_class(class_id)
