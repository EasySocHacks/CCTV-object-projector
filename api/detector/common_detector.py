from abc import ABC, abstractmethod


class CommonDetector(ABC):
    def __init__(self, device):
        self.device = device

    @abstractmethod
    def detect(self, image):
        pass

    @staticmethod
    @abstractmethod
    def decode_class(class_id: int):
        pass
