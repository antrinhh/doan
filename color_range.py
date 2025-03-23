import cv2
import numpy as np


def nothing(x):
    pass


image = cv2.imread("blue_.jpg")
image = cv2.resize(image, (640, 480))

cv2.namedWindow("color range")

cv2.createTrackbar('L min', 'color range', 0, 255, nothing)
cv2.createTrackbar('a min', 'color range', 0, 255, nothing)
cv2.createTrackbar('b min', 'color range', 0, 255, nothing)
cv2.createTrackbar('L max', 'color range', 0, 255, nothing)
cv2.createTrackbar('a max', 'color range', 0, 255, nothing)
cv2.createTrackbar('b max', 'color range', 0, 255, nothing)

cv2.setTrackbarPos('L max', 'color range', 255)
cv2.setTrackbarPos('a max', 'color range', 255)
cv2.setTrackbarPos('b max', 'color range', 255)

L_min = a_min = b_min = L_max = a_max = b_max = 0
while True:
    L_min = cv2.getTrackbarPos('L min', 'color range')
    a_min = cv2.getTrackbarPos('a min', 'color range')
    b_min = cv2.getTrackbarPos('b min', 'color range')
    L_max = cv2.getTrackbarPos('L max', 'color range')
    a_max = cv2.getTrackbarPos('a max', 'color range')
    b_max = cv2.getTrackbarPos('b max', 'color range')

    lower = np.array([L_min, a_min, b_min])
    upper = np.array([L_max, a_max, b_max])
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    mask = cv2.inRange(lab, lower, upper)
    result = cv2.bitwise_and(image, image, mask=mask)

    cv2.imshow('color range', result)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
