import random

from bbox_expander.bbox_expander import BboxExpander


class BboxExpanderPool:
    def __init__(self, size: int, device, bbox_expander_type=BboxExpander):
        self.size = size
        self.device = device
        self.bbox_expander_type = bbox_expander_type

        self.bbox_expander_pool = []
        for i in range(size):
            self.bbox_expander_pool.append(bbox_expander_type(device))

    def expand(self, image, bbox_expander_number=None):
        if bbox_expander_number is None:
            return self.bbox_expander_pool[random.randint(0, self.size - 1)].expand(image)
        else:
            return self.bbox_expander_pool[bbox_expander_number].expand(image)
