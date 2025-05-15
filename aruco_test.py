import cv2
import numpy as np
from aruco_detect import homo_matrix_from_marker
from aruco_axis import show_distance, show_matrix, show_coords
from matrixes import ForwardKinematics, Homogeous_end_to_cam


H_0to4 = ForwardKinematics(30, 60, 120, 60)
H_4tocam = Homogeous_end_to_cam()
cap = cv2.VideoCapture(2)
while True:
    ret, frame = cap.read()
    H_cam2obj = homo_matrix_from_marker(frame)
    if H_cam2obj is not None:
        H = np.dot(np.dot(H_0to4, H_4tocam), H_cam2obj)
        show_distance(frame, H_cam2obj)
        show_matrix(frame, "H obj to base", H)
        show_matrix(frame, "H cam to obj", H_cam2obj, start_y=230)
        show_coords(frame, H)
    cv2.imshow("video", frame)
    if cv2.waitKey(16) == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
