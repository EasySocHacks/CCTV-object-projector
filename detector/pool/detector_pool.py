import random
from typing import List

from detector.common_detector import CommonDetector


class DetectorPool:
    def __init__(self, size: int, detector_type: CommonDetector):
        self.size = size
        self.detector_type = detector_type

        self.pool: List[CommonDetector] = []
        for pool_id in range(size):
            self.pool.append(detector_type.__init__())

    def detect(self, image):
        return self.pool[random.randint(0, self.size - 1)].detect(image)

    def decode_class(self, class_id: int):
        return self.detector_type.decode_class(class_id)
