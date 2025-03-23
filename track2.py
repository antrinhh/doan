import cv2
import numpy as np
import time
from KalmanFilter import KalmanFilter
from imutils.video import FPS

fps = None
start_time = time.time()
video = cv2.VideoCapture(0)
KF = KalmanFilter(0.05)
while True:
    current_time = time.time()
    t = current_time - start_time
    print(t)
    KF.dt = t
    start_time = time.time()
    ret, frame = video.read()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, (0, 0, 0), (180, 255, 50))
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 300:
            (x_con, y_con), radius = cv2.minEnclosingCircle(contour)
            # cv2.circle(frame, (int(x_con), int(y_con)), int(radius) + 2, (0, 255, 0), 2)
            KF.predict()
            # cv2.circle(
            #     frame,
            #     (int(KF.x[0]), int(KF.x[1])),
            #     int(radius) + 2,
            #     (0, 255, 0),
            #     2,
            # )
    KF.correct(int(x_con), int(y_con))
    cv2.circle(
        frame,
        (int(KF.x[0]), int(KF.x[1])),
        int(radius) + 2,
        (0, 0, 255),
        2,
    )
    if fps is None:
        fps = FPS().start()

    fps.update()

    fps.stop()
    fps_text = f"FPS: {fps.fps():.2f}"
    cv2.putText(frame, fps_text, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.namedWindow("video", cv2.WINDOW_NORMAL)

    cv2.resizeWindow("video", 640, 480)
    cv2.imshow("video", frame)

    if cv2.waitKey(16) == ord("q"):
        break
video.release()
cv2.destroyAllWindows()
