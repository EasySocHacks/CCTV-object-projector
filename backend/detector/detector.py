from abc import ABC, abstractmethod


class Detector(ABC):
    def __init__(self, device):
        self.device = device

    @abstractmethod
    def detect(self, image):
        pass

    @staticmethod
    @abstractmethod
    def model_from_str(model_name, model_weight_path=None):
        pass
