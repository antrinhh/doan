import cv2
import numpy as np
import glob

criteria = (cv2.TermCriteria_EPS+cv2.TermCriteria_MAX_ITER, 30, 0.001)

objp = np.zeros((7*7, 3), np.float32)
objp[:, :2] = (np.mgrid[0:7, 0:7].T.reshape(-1, 2))*1.6
objpoints = []
imgpoints = []
images = glob.glob("calibrate/*.jpg")

for image in images:
    img = cv2.imread(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, (7, 7), None)
    if not ret:
        print(f"Không tìm thấy góc trên ảnh: {image}")

    if ret == True:
        objpoints.append(objp)
        corners2 = cv2.cornerSubPix(
            gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2)
        cv2.drawChessboardCorners(img, (7, 7), corners2, ret)
        cv2.imshow("image", img)
        cv2.waitKey(0)
cv2.destroyAllWindows()
ret, cam_mtx, dist, rot_vec, trans_vec = cv2.calibrateCamera(
    objpoints, imgpoints, gray.shape[::-1], None, None)
# np.savez("B.npz", cam_mtx=cam_mtx, dist=dist,
#           rot_vec=rot_vec, trans_vec=trans_vec)
print(ret)
