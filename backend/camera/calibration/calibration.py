import numpy as np


class Calibration:
    def __init__(self, screen_points, world_points):
        self.screen_points = screen_points
        self.world_points = world_points

        x = screen_points[:, 0]
        y = screen_points[:, 1]

        X = world_points[:, 0]
        Y = world_points[:, 1]
        Z = world_points[:, 2]

        a_x = np.array([
            -X, -Y, -Z, -np.ones(6),
            np.zeros(6), np.zeros(6), np.zeros(6), np.zeros(6),
            x * X, x * Y, x * Z, x
        ])

        a_y = np.array([
            np.zeros(6), np.zeros(6), np.zeros(6), np.zeros(6),
            -X, -Y, -Z, -np.ones(6),
            y * X, y * Y, y * Z, y
        ])

        M = np.empty((2 * 6, 12))
        M[::2, :] = a_x.T
        M[1::2, :] = a_y.T

        U, S, V = np.linalg.svd(M)

        P = V[-1, :].reshape((3, 4))

        self.matrix = P

    def project_3d_to_2d(self, coord):
        a, b, c = self.matrix @ np.append(coord, np.ones(1)).T

        return np.array([a / c, b / c])

    def project_2d_to_3d_homo(self, coord):
        M = np.array([
            [self.matrix[2, 0] * coord[0] - self.matrix[0, 0], self.matrix[2, 1] * coord[0] - self.matrix[0, 1]],
            [self.matrix[2, 0] * coord[1] - self.matrix[1, 0], self.matrix[2, 1] * coord[1] - self.matrix[1, 1]]
        ])
        v = np.array([
            self.matrix[0, 3] - self.matrix[2, 3] * coord[0],
            self.matrix[1, 3] - self.matrix[2, 3] * coord[1]
        ])

        X, Y = np.linalg.solve(M, v)

        return np.array([X, Y, 0])
