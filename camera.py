import cv2 as cv
from aruco_detect import homo_matrix_from_marker
import numpy as np
from matrixes import Homogeous_end_to_cam

# Load camera calibration parameters
with np.load('calibration.npz') as X:
    cam_matrix, dist_coeffs = [X[i] for i in ('cam_mtx', 'dist')]
cap = cv.VideoCapture(1)
last_box = None  # Store last known box coordinates
H_end_cam = Homogeous_end_to_cam()
H_cam_obj = np.eye(4)
H_end_obj = np.eye(4)
trans_end_zones = np.zeros((3, 1))
while True:
    ret, frame = cap.read()
    if not ret:
        break
    copy = frame.copy()
    # cv.circle(copy, (329, 231), radius=30, color=(0, 0, 255), thickness=1)
    # cv.line(copy, (299, 231), (359, 231),(0, 0, 255), 1)
    # cv.line(copy, (329, 201), (329, 261),(0, 0, 255), 1)
    # frame[231, 329] = (0, 0, 255)
    # Detect marker and get homography + bounding box
    H_cam_obj, box = homo_matrix_from_marker(frame, cam_matrix, dist_coeffs, drawAxis=True)
    # print(f"[DEBUG] Marker detection: H={H_cam_obj is not None}, box={box}")

    # If new box is found, update last known box
    if H_cam_obj is not None and box is not None:
        H_end_obj = H_end_cam.dot(H_cam_obj)
        trans_end_zones = H_end_obj[:3, 3]
        print(f"trans {trans_end_zones}") 
        last_box = box

    roi = None
    if last_box:
        x_min, y_min, x_max, y_max = last_box
        x_min = max(x_min - 5, 0)
        y_min = max(y_min - 80, 0)
        x_max = min(x_max + 55, frame.shape[1])
        y_max = min(y_max + 10, frame.shape[0])
        roi = frame[y_min:y_max, x_min:x_max]

    # Show the last ROI on the current frame
    if roi is not None and roi.size > 0:
        cv.imshow("roi", roi)

    cv.imshow("frame", frame)

    if cv.waitKey(1) == ord('q'):
        break

cap.release()
cv.destroyAllWindows()
