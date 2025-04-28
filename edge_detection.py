import cv2
import numpy as np


def draw(img, image_points, imgpts):
    corner = tuple(map(int, image_points[0].ravel()))
    img = cv2.line(img, corner, tuple(
        np.int32(imgpts[0].ravel())), (255, 0, 0), 5)
    img = cv2.line(img, corner, tuple(
        np.int32(imgpts[1].ravel())), (0, 255, 0), 5)
    img = cv2.line(img, corner, tuple(
        np.int32(imgpts[2].ravel())), (0, 0, 255), 5)

    return img


with np.load("calibrate/B.npz") as X:
    cam_mtx, dist, _, _ = [X[i]
                           for i in ('cam_mtx', 'dist', 'rot_vec', 'trans_vec')]


size = 2.5
object_points = np.array([
    [0, 0, 0],
    [size, 0, 0],
    [size, size, 0],
    [0, size, 0]
], dtype=np.float32)

imgpoints = []
axis = np.float32([[2.5, 0, 0], [0, 2.5, 0], [0, 0, 2.5]]).reshape(-1, 3)
# cap = cv2.VideoCapture(2)
# while True:
#     ret, image = cap.read()
image_path = "data/objs.jpg"
image = cv2.imread(image_path)

lower = np.array([82, 153, 138])
upper = np.array([255, 255, 255])
lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
mask = cv2.inRange(lab, lower, upper)
new_img = cv2.bitwise_and(image, image, mask=mask)
cv2.imshow("bitwise", new_img)

gray = cv2.cvtColor(new_img, cv2.COLOR_BGR2GRAY)

blurred = cv2.GaussianBlur(gray, (5, 5), 0)

edges = cv2.Canny(blurred, 50, 150)
cv2.imshow("edge dt", edges)
contours, _ = cv2.findContours(
    edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

for cnt in contours:
    if cv2.contourArea(cnt) > 50:
        epsilon = 0.02 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        # cv2.drawContours(image, [approx], -1, (0, 255, 0), 2)

        if len(approx) == 4:
            for point in approx:
                cv2.circle(image, tuple(point[0]), 5, (0, 0, 255), -1)
            # print("Tọa độ 4 đỉnh:", approx.reshape(4, 2))
            # reordered_points = approx[[2, 1, 0, 3]]
            imgpoints.append(approx.reshape(4, 2))
            # imgpoints = [(reordered_points.reshape(4, 2))]

for i in range(len(imgpoints)):
    ret, rvec, tvec = cv2.solvePnP(object_points, np.array(
        imgpoints[i], dtype=np.float32), cam_mtx, dist)
    imgpts, jac = cv2.projectPoints(axis, rvec, tvec, cam_mtx, dist)
    image = draw(image, imgpoints[i], imgpts)

cv2.imshow("Detected Corners", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
#     if cv2.waitKey(16) == ord('q'):
#         break
# cap.release()
# cv2.destroyAllWindows()
