import numpy as np


class Calibration:
    def __init__(self, matrix):
        self.matrix = matrix

    def project_3d_to_2d(self, coord):
        a, b, c = self.matrix @ np.append(coord, np.ones(1)).T

        return np.array([a / c, b / c])

    def project_2d_to_3d_homo(self, coord):
        a, b, c, d = self.matrix.T @ np.append(coord, np.ones(1))

        return np.array([(a - c) / (d - c), (b - c) / (d - c), 0])
