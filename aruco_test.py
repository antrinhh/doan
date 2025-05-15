import cv2
import numpy as np
from aruco_detect import homo_matrix_from_marker
from aruco_axis import show_distance, show_matrix


cap = cv2.VideoCapture(2)
while True:
    ret, frame = cap.read()
    H = homo_matrix_from_marker(frame)
    show_distance(frame, H)
    show_matrix(frame, H)
    cv2.imshow("video", frame)
    if cv2.waitKey(16) == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
