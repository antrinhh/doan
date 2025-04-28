import cv2
import numpy as np
import glob

criteria = (cv2.TermCriteria_EPS+cv2.TermCriteria_MAX_ITER, 30, 0.001)

with np.load("calibrate/B.npz") as X:
    cam_mtx, dist, _, _ = [X[i]
                           for i in ('cam_mtx', 'dist', 'rot_vec', 'trans_vec')]


def draw(img, corners, imgpts):
    corner = tuple(map(int, corners[0].ravel()))
    img = cv2.line(img, corner, tuple(
        map(int, imgpts[0].ravel())), (255, 0, 0), 5)
    img = cv2.line(img, corner, tuple(
        map(int, imgpts[1].ravel())), (0, 255, 0), 5)
    img = cv2.line(img, corner, tuple(
        map(int, imgpts[2].ravel())), (0, 0, 255), 5)
    return img


objp = np.zeros((7*7, 3), np.float32)
objp[:, :2] = np.mgrid[0:7, 0:7].T.reshape(-1, 2)
axis = np.float32([[3, 0, 0], [0, 3, 0], [0, 0, -3]]).reshape(-1, 3)
for fname in glob.glob('calibrate/*.jpg'):
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, (7, 7), None)
    if ret == True:
        corners2 = cv2.cornerSubPix(
            gray, corners, (11, 11), (-1, -1), criteria)
        ret, rvec, tvec = cv2.solvePnP(objp, corners2, cam_mtx, dist)
        imgpts, jac = cv2.projectPoints(axis, rvec, tvec, cam_mtx, dist)
        img = draw(img, corners2, imgpts)
        cv2.imshow("image", img)
        cv2.waitKey(0)
cv2.destroyAllWindows()
