import cv2
import numpy as np


def draw(img, image_points, imgpts):
    corner = tuple(map(int, image_points[0].ravel()))
    img = cv2.line(img, corner, tuple(
        np.int32(imgpts[0].ravel())), (255, 0, 0), 2)
    img = cv2.line(img, corner, tuple(
        np.int32(imgpts[1].ravel())), (0, 255, 0), 2)
    img = cv2.line(img, corner, tuple(
        np.int32(imgpts[2].ravel())), (0, 0, 255), 2)

    return img


img = cv2.imread("data/red 1.jpg")
img = cv2.resize(img, (604, 504))
height, width, _ = img.shape
lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
lower = np.array([0, 144, 136])
upper = np.array([255, 255, 255])
mask = cv2.inRange(lab, lower, upper)
kernel = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]])
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
new = cv2.bitwise_and(img, img, mask=mask)


new[:, :, 0] = 0
new[:, :, 1] = 0
red_channel = new[:, :, 2]
color_thr1 = new.copy()
color_thr2 = new.copy()

for y in range(height):
    for x in range(width):
        # if color_thr[y, x, 2] > 190 or color_thr[y, x, 2] < 140:
        #     color_thr[y, x, 2] = 0
        # if color_thr[y, x, 2] > 140:
        #     color_thr[y, x, 2] = 0
        if color_thr1[y, x, 2] < 190:
            color_thr1[y, x, 2] = 0

color_thr1 = cv2.morphologyEx(color_thr1, cv2.MORPH_OPEN, kernel)
color_thr1 = cv2.morphologyEx(color_thr1, cv2.MORPH_CLOSE, kernel)
color_thr1 = cv2.dilate(color_thr1, kernel)
edge = cv2.Canny(color_thr1, 150, 200)
contours, _ = cv2.findContours(
    edge, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

point1 = []
point2 = []

for contour in contours:
    epsilon = 0.03*cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)
    if len(approx) == 4:
        for point in approx:
            # cv2.circle(img, tuple(point[0]), 3, (0, 255, 0), 1)
            point1.append(list(point[0]))


for y in range(height):
    for x in range(width):
        # if color_thr[y, x, 2] > 190 or color_thr[y, x, 2] < 140:
        #     color_thr[y, x, 2] = 0
        if color_thr2[y, x, 2] > 140:
            color_thr2[y, x, 2] = 0
        # if color_thr1[y, x, 2] < 190:
        #     color_thr1[y, x, 2] = 0

color_thr2 = cv2.morphologyEx(color_thr2, cv2.MORPH_OPEN, kernel)
color_thr2 = cv2.morphologyEx(color_thr2, cv2.MORPH_CLOSE, kernel)
color_thr2 = cv2.dilate(color_thr2, kernel)
edge = cv2.Canny(color_thr2, 150, 200)
contours, _ = cv2.findContours(
    edge, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

for contour in contours:
    epsilon = 0.03*cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)
    if len(approx) == 4:
        for point in approx:
            # cv2.circle(img, tuple(point[0]), 3, (0, 255, 0), 1)
            point2.append(list(point[0]))


for point_1 in point1:
    for point_2 in point2:
        if abs(point_1[0] - point_2[0]) < 20:
            if abs(point_1[1] - point_2[1]) < 20:
                point_1[0] = int((point_1[0]+point_2[0])/2)
                point_1[1] = int((point_1[1]+point_2[1])/2)
                point2.remove(point_2)

point1 = point1+point2
point1 = np.array(point1)[[2, 5, 4, 1, 0, 3]]
print(point1)

for point in point1:
    cv2.circle(img, tuple(point), 4, (0, 0, 0), -1)


with np.load("calibrate/B.npz") as X:
    cam_mtx, dist, _, _ = [X[i]
                           for i in ('cam_mtx', 'dist', 'rot_vec', 'trans_vec')]

size = 2.5
object_points = np.array([
    [0, 0, 0],
    [size, 0, 0],
    [size, 0, size],
    [0, 0, size],
    [0, size, size],
    [0, size, 0]
], dtype=np.float32)
axis = np.float32([[2.5, 0, 0], [0, 2.5, 0], [0, 0, 2.5]]).reshape(-1, 3)

for i in range(len(point1)):
    ret, rvec, tvec = cv2.solvePnP(object_points, np.array(
        point1, dtype=np.float32), cam_mtx, dist)
    imgpts, jac = cv2.projectPoints(axis, rvec, tvec, cam_mtx, dist)
    img = draw(img, point1, imgpts)

cv2.imshow("edge", edge)
# cv2.imshow("mask", mask)
cv2.imshow("threshold", new)
cv2.imshow("image", color_thr1)
cv2.imshow("img", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
