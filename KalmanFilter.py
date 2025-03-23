import numpy as np


class KalmanFilter:
    def __init__(self, dt):
        self.dt = dt
        self.u = np.array([[0.1], [0.1]])
        self.x = np.array([[0], [0], [0], [0]])
        self.H = np.array([[1, 0, 0, 0], [0, 1, 0, 0]])
        self.A = np.array(
            [[1, 0, self.dt, 0], [0, 1, 0, self.dt], [0, 0, 1, 0], [0, 0, 0, 1]]
        )
        self.St = (
            np.array(
                [
                    [(self.dt**4) / 4, 0, 0, 0],
                    [0, (self.dt**4) / 4, 0, 0],
                    [0, 0, self.dt**2, 0],
                    [0, 0, 0, self.dt**2],
                ]
            )
            * 1000000
        )
        self.B = np.array(
            [[(self.dt**2) / 2, 0], [0, (self.dt**2) / 2], [self.dt, 0], [0, self.dt]]
        )
        self.Q = np.array(
            [
                [0.25 * (self.dt**4), 0, 0.5 * (self.dt**3), 0],
                [0, 0.25 * (self.dt**4), 0, 0.5 * (self.dt**3)],
                [0.5 * (self.dt**3), 0, self.dt**2, 0],
                [0, 0.5 * (self.dt**3), 0, self.dt**2],
            ]
        )
        self.R = np.array([[0.001, 0], [0, 0.001]])
        self.I = np.eye(4)

    def predict(self):
        self.x = np.dot(self.A, self.x) + np.dot(self.B, self.u)
        self.St = np.dot(np.dot(self.A, self.St), self.A.T) + self.Q

    def correct(self, x_meas, y_meas):
        Y = np.array([[x_meas], [y_meas]])
        V = np.dot(np.dot(self.H, self.St), self.H.T) + self.R
        self.K = np.dot(np.dot(self.St, self.H.T), np.linalg.inv(V))
        self.x = self.x + np.dot(self.K, Y - np.dot(self.H, self.x))
        self.St = np.dot(self.I - np.dot(self.K, self.H), self.St)
