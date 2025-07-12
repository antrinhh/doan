import cv2
import numpy as np
import cv2.aruco as aruco
from matrixes import z_180
import math


size = 25
obj_points = np.array([[0, 0, 0], [-size/2, -size/2, 0], [-size/2, size/2, 0],
                      [size/2, size/2, 0], [size/2, -size/2, 0]], dtype=np.float32)


with np.load('/home/siuw/Documents/doan/calibration.npz') as X:
    cam_mtx, dist = [X[i] for i in ('cam_mtx', 'dist')]
ARUCO_DICT = aruco.getPredefinedDictionary(aruco.DICT_5X5_1000)

# Colors
RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)


def draw_axis(img, start_pts, img_pts):
    start_point = list(start_pts[0].ravel().astype(int))
    end_point_x = list(img_pts[0].ravel().astype(int))
    end_point_y = list(img_pts[1].ravel().astype(int))
    end_point_z = list(img_pts[2].ravel().astype(int))

    cv2.arrowedLine(img, start_point, end_point_x, RED, 2)
    cv2.arrowedLine(img, start_point, end_point_y, GREEN, 2)
    cv2.arrowedLine(img, start_point, end_point_z, BLUE, 2)

    end_point_x[0] = end_point_x[0] + 10
    end_point_y[1] = end_point_y[1] - 10
    end_point_z[1] = end_point_z[1] + 10
    end_point_z[0] = end_point_z[0] - 10

    cv2.putText(img, 'x', end_point_x, cv2.FONT_HERSHEY_PLAIN,
                0.8, RED, 1, cv2.LINE_AA)
    cv2.putText(img, 'y', end_point_y, cv2.FONT_HERSHEY_PLAIN,
                0.8, GREEN, 1, cv2.LINE_AA)
    cv2.putText(img, 'z', end_point_z, cv2.FONT_HERSHEY_PLAIN,
                0.8, BLUE, 1, cv2.LINE_AA)


def show_distance(frame, H=None):
    if H is not None:
        x, y, z = H[:3, 3].flatten()
        distance = math.sqrt(x**2+y**2+z**2)
        cv2.putText(frame, f"distance to cam: {distance:.3f}mm", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)


def show_matrix(frame, text, H=None, start_y=50):
    if H is not None:
        cv2.putText(frame, f"{text}:", (410, start_y-20),
                    cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)
        dy = 20
        font = cv2.FONT_HERSHEY_PLAIN
        for i in range(H.shape[0]):
            text = f"{H[i][0]: .2f} {H[i][1]: .2f} {H[i][2]: .2f} {H[i][3]: .2f}"
            y = start_y + i * dy
            cv2.putText(frame, text, (410, y), cv2.FONT_HERSHEY_PLAIN,
                        1, (0, 0, 255), 2)


def show_coords(frame, H=None):
    if H is not None:
        x, y, z = H[:3, 3].flatten()
        cv2.putText(frame, f"Toa do trong he base:", (410, 130),
                    cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)
        cv2.putText(frame, f"x: {x:.2f}", (410, 150),
                    cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)
        cv2.putText(frame, f"y: {y:.2f}", (410, 170),
                    cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)
        cv2.putText(frame, f"z: {z:.2f}", (410, 190),
                    cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)


def homo_matrix_from_marker(frame, camera_matrix=cam_mtx, dist=dist, object_pts=obj_points, drawAxis=True, aruco_dict=ARUCO_DICT):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    corners, ids, _ = aruco.detectMarkers(
        gray, aruco_dict, camera_matrix, dist)
    if len(corners) or ids is not None:
        aruco.drawDetectedMarkers(frame, corners)

        marker_corners = corners[0][0]  # shape: (4, 2)
        x_min = int(np.min(marker_corners[:, 0]))
        x_max = int(np.max(marker_corners[:, 0]))
        y_min = int(np.min(marker_corners[:, 1]))
        y_max = int(np.max(marker_corners[:, 1]))
        bounding_box = (x_min, y_min, x_max, y_max)

        center = np.array((abs(corners[0][0][2][0] + corners[0][0][0][0])//2,
                           abs(corners[0][0][2][1] + corners[0][0][0][1])//2)).astype(int)
        point = np.vstack((center, corners[0][0]))
        for idx, p in enumerate(point):
            pos = tuple(p.astype(int))  # ensure (x, y) integer format
            cv2.circle(frame, pos, 5, (255, 0, 0), -1)  # draw blue dot
            cv2.putText(frame, str(idx), (pos[0] + 5, pos[1] - 5),  # slight offset
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv2.LINE_AA)  # yellow text

        retval, rvec, tvec = cv2.solvePnP(
            object_pts, point, camera_matrix, dist)
        if drawAxis == True:
            axis = np.array([[25, 0, 0], [0, 25, 0], [
                            0, 0, 25]], dtype=np.float32)
            img_pts, jac = cv2.projectPoints(
                axis, rvec, tvec, camera_matrix, dist)
            draw_axis(frame, point, img_pts)
        if retval:
            R, _ = cv2.Rodrigues(rvec)
            H = np.hstack((R, tvec))
            H = np.vstack((H, np.array([0, 0, 0, 1])))
            return H, bounding_box
    else:
        return None, None
