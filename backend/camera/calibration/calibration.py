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

        H = P[:, :3]
        h = P[:, 3]

        self.camera_coordinates = -np.linalg.inv(H) @ h

    def project_3d_to_2d(self, coord):
        a, b, c = self.matrix @ np.append(coord, np.ones(1)).T

        return np.array([a / c, b / c])

    def project_2d_to_3d_homo(self, coord):
        a, b, c, d = self.matrix.T @ np.append(coord, np.ones(1))

        detect_3d = np.array([a / d, b / d, c / d])

        vec = detect_3d - self.camera_coordinates

        k = self.camera_coordinates[2] / vec[2]

        return self.camera_coordinates + vec * k
