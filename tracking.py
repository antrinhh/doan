import cv2
import numpy as np
import time

u = np.array([[0.1], [0.1]])
x = np.array([[0], [0], [0], [0]])
H = np.array([[1, 0, 0, 0], [0, 1, 0, 0]])
R = np.array([[0.001, 0], [0, 0.001]])
I = np.eye(4)
start_time = time.time()
video = cv2.VideoCapture(0)
while True:
    current_time = time.time()
    dt = current_time - start_time
    start_time = time.time()
    A = np.array([[1, 0, dt, 0], [0, 1, 0, dt], [0, 0, 1, 0], [0, 0, 0, 1]])
    B = np.array([[0.5 * (dt**2), 0], [0, 0.5 * (dt**2)], [dt, 0], [0, dt]])
    St = (
        np.array(
            [
                [0.25 * (dt**4), 0, 0, 0],
                [0, 0.25 * (dt**4), 0, 0],
                [0, 0, dt**2, 0],
                [0, 0, 0, dt**2],
            ]
        )
        * 1000000
    )
    Q = np.array(
        [
            [0.25 * (dt**4), 0, 0.5 * (dt**3), 0],
            [0, 0.25 * (dt**4), 0, 0.5 * (dt**3)],
            [0.5 * (dt**3), 0, dt**2, 0],
            [0, 0.5 * (dt**3), 0, dt**2],
        ]
    )
    ret, frame = video.read()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    mask = cv2.inRange(hsv, (0, 118, 70), (188, 255, 117))
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 300:
            (x_con, y_con), radius = cv2.minEnclosingCircle(contour)
            # cv2.circle(frame, (int(x_con), int(y_con)), int(radius) + 2, (0, 255, 0), 2)
            Y = np.array([[int(x_con)], [int(y_con)]])
            x = np.dot(A, x) + np.dot(B, u)
            St = np.dot(np.dot(A, St), A.T) + Q
    if "Y" in locals():
        V = np.dot(np.dot(H, St), H.T) + R
        K = np.dot(np.dot(St, H.T), np.linalg.inv(V))
        x = x + np.dot(K, Y - np.dot(H, x))
        St = np.dot(I - np.dot(K, H), St)
        cv2.circle(frame, (int(x[0]), int(x[1])),
                   int(radius) + 2, (0, 0, 255), 2)
    cv2.imshow("video", frame)
    if cv2.waitKey(1) == ord("q"):
        break
video.release()
cv2.destroyAllWindows()
