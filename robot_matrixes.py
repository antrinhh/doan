import numpy as np

def compute_A(q1, q2, q3, q4):
    A = np.array([
        [
            np.cos(q2 + q3 + q4 + q1),
            -np.sin(q2 + q3 + q4 + q1),
            0,
            140*np.cos(q2 + q1) + 140*np.cos(q2 + q3 + q1) + 70*np.cos(q2 + q3 + q4 + q1)
        ],
        [
            np.sin(q2 + q3 + q4 + q1),
            np.cos(q2 + q3 + q4 + q1),
            0,
            140*np.sin(q2 + q1) + 140*np.sin(q2 + q3 + q1) + 70*np.sin(q2 + q3 + q4 + q1)
        ],
        [
            np.sin(q2 + q3 + q4),
            np.cos(q2 + q3 + q4),
            0,
            140*np.sin(q2) + 140*np.sin(q2 + q3) + 70*np.sin(q2 + q3 + q4) + 120
        ],
        [
            0,
            0,
            0,
            1
        ]
    ])
    return A
