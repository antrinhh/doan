import cv2
import numpy as np
import cv2.aruco as aruco
from aruco_axis import draw_axis
import math


size = 7.8
obj_points = np.array([[0, 0, 0], [-size/2, -size/2, 0], [-size/2, size/2, 0],
                      [size/2, size/2, 0], [size/2, -size/2, 0]], dtype=np.float32)


with np.load('B.npz') as X:
    cam_mtx, dist = [X[i] for i in ('cam_mtx', 'dist')]
ARUCO_DICT = aruco.getPredefinedDictionary(aruco.DICT_4X4_250)


def homo_matrix_from_marker(frame, camera_matrix=cam_mtx, dist=dist, object_pts=obj_points, drawAxis=True, aruco_dict=ARUCO_DICT):

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    corners, ids, _ = aruco.detectMarkers(
        gray, aruco_dict, camera_matrix, dist)
    if len(corners) or ids is not None:
        aruco.drawDetectedMarkers(frame, corners)
        center = np.array((abs(corners[0][0][2][0] + corners[0][0][0][0])//2,
                           abs(corners[0][0][2][1] + corners[0][0][0][1])//2)).astype(int)
        point = np.vstack((center, corners[0][0]))
        retval, rvec, tvec = cv2.solvePnP(
            object_pts, point, camera_matrix, dist)
        if drawAxis == True:
            axis = np.array([[2.5, 0, 0], [0, 2.5, 0], [
                            0, 0, 2.5]], dtype=np.float32)
            img_pts, jac = cv2.projectPoints(
                axis, rvec, tvec, camera_matrix, dist)
            draw_axis(frame, point, img_pts)
        if retval:
            R, _ = cv2.Rodrigues(rvec)
            H = np.hstack((R, tvec))
            H = np.vstack((H, np.array([0, 0, 0, 1])))
            return H
    else:
        return None
