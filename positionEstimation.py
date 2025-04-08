import cv2 as cv
import numpy as np
import os
import argparse

def nothing(x):
    pass

parse = argparse.ArgumentParser()
parse.add_argument("Color", type=str, help="Color want to detect")

cv.namedWindow("color range")

cv.createTrackbar('L min', 'color range', 0, 255, nothing)
cv.createTrackbar('a min', 'color range', 0, 255, nothing)
cv.createTrackbar('b min', 'color range', 0, 255, nothing)
cv.createTrackbar('L max', 'color range', 0, 255, nothing)
cv.createTrackbar('a max', 'color range', 0, 255, nothing)
cv.createTrackbar('b max', 'color range', 0, 255, nothing)

cv.setTrackbarPos('L max', 'color range', 255)
cv.setTrackbarPos('a max', 'color range', 255)
cv.setTrackbarPos('b max', 'color range', 255)
cv.setTrackbarPos('b min', 'color range', 113)

L_min = a_min = b_min = L_max = a_max = b_max = 0
# cap = cv.VideoCapture("data/red vid.MOV")
# ret, img = cap.read()
img = cv.imread("data/image.png")
img = cv.resize(img, (720, 480))
lab = cv.cvtColor(img, cv.COLOR_BGR2LAB)

while True:
    
    
    L_min = cv.getTrackbarPos('L min', 'color range')
    a_min = cv.getTrackbarPos('a min', 'color range')
    b_min = cv.getTrackbarPos('b min', 'color range')
    L_max = cv.getTrackbarPos('L max', 'color range')
    a_max = cv.getTrackbarPos('a max', 'color range')
    b_max = cv.getTrackbarPos('b max', 'color range')
    upper = np.array([L_max, a_max, b_max])
    lower = np.array([L_min, a_min, b_min])

    mask = cv.inRange(lab, lower, upper)

    kernel = np.ones((3,3))
    mask1 = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)
    kernel = np.ones((3,3))
    mask2 = cv.morphologyEx(mask1, cv.MORPH_ERODE, kernel)

    mask2 = 255 - mask2  # This is the final goal, this mask will represent the cube in the frame
    lab_threshold = cv.bitwise_and(lab, lab, mask = mask2)
    bgr_threshold = cv.bitwise_and(img, img, mask = mask2)

    ##################################################################

    gray = cv.cvtColor(bgr_threshold, cv.COLOR_BGR2GRAY)

    contours, hierachy = cv.findContours(gray, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

    if contours:
        for contour in contours:
            eps = 0.02*cv.arcLength(contour, True)
            approx = cv.approxPolyDP(contour, eps, True)
            cv.polylines(img, [approx], True, (0, 0, 255), 3)
            # cv.drawContours(img, approx, -1, (0, 0, 255), 3)
    # cv.drawContours(img, contours, -1, (0, 0, 255), 3)
    # for contour in contours:
        # epsilon = 0.1*cv.arcLength(contour, True)
        # approx = cv.approxPolyDP(contour, epsilon, True)
        # cv.drawContours(bgr_threshold, contour, -1, (0, 255, 0), 1)

    cv.imshow('result', img)
    cv.imshow('result2', bgr_threshold)

    if cv.waitKey(50) == ord('q'):
        break
cv.destroyAllWindows()
