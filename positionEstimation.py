import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
import os
import argparse

def nothing(x):
    pass

def load_calibration():
    param_path = os.path.join(os.getcwd(), 'calibration.npz')
    param_data = np.load(param_path)
    return param_data['camMatrix'], param_data['distCoeff']


cube_size = 2.5
cube_points = np.array([[0, 0, 0], [cube_size, 0, 0], [cube_size, 0, -cube_size], 
                        [cube_size, cube_size, -cube_size], [0, cube_size, -cube_size], [0, cube_size, 0],
                          [0, 0, -cube_size], [cube_size, cube_size, 0]], dtype=float)

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

cam_matrix, dist_coeffs = load_calibration()

L_min = a_min = b_min = L_max = a_max = b_max = 0
cap = cv.VideoCapture(1)
#img = cv.imread("data/image.png")
#img = cv.resize(img, (720, 480))

while True:
    ret, img = cap.read()
    img = cv.resize(img, (720, 480))
    lab = cv.cvtColor(img, cv.COLOR_BGR2LAB)
    
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
    kernel = np.ones((1,1))
    mask2 = cv.morphologyEx(mask1, cv.MORPH_ERODE, kernel)

    mask2 = 255 - mask2  # This is the final goal, this mask will represent the cube in the frame
    img_copy = img.copy()
    lab_threshold = cv.bitwise_and(lab, lab, mask = mask2)
    bgr_threshold = cv.bitwise_and(img_copy, img_copy, mask = mask2)

    
    # Cutting out grayscale and get the cube for sure area
    gray = cv.cvtColor(bgr_threshold, cv.COLOR_BGR2GRAY)

    contours, hierachy = cv.findContours(gray, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

    approx = None
    text = "Default: None"
    if contours:
        for contour in contours:
            eps = 0.02*cv.arcLength(contour, True)
            approx = cv.approxPolyDP(contour, eps, True) # Cube's corners approxiamte and from there get the cube approx area
            cv.polylines(img_copy, [approx], True, (0, 0, 255), 3)
            x, y, w, h = cv.boundingRect(approx)
            if approx is not None and len(approx) >= 4:
                cv.polylines(img_copy, [approx], True, (0, 0, 255), 3)
                for i, point in enumerate(approx):
                    x, y = point[0]
                    cv.circle(img_copy, (x, y), 5, (0, 255, 0), -1)
                    cv.putText(img_copy, str(i), (x + 5, y - 5), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                try:
                    retval, rvec, tvec = cv.solvePnP(cube_points[:len(approx)], approx.astype(np.float32), cam_matrix, dist_coeffs)
                    distance = np.linalg.norm(tvec)
                    text = f"Distance to camera: {distance:.2f} cm"
                except:
                    text = "solvePnP failed"
            else:
                text = "Not enough corners"

    text_position = (10, img.shape[0] - 10)
    cv.putText(img_copy, text, text_position, cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv.LINE_AA)
            
    # approx_mask = np.zeros(img.shape[:2], dtype=np.uint8)
    # cv.fillPoly(approx_mask, [approx], 255)
    # masked_gray = cv.bitwise_and(gray, gray, mask=approx_mask) #grayscale cut-out

    # # Draw approximate corners
    # index = 0
    # for point in approx:
    #     x, y = point[0]
    #     cv.circle(img_copy, (x, y), 5, (0, 255, 0), -1)
    #     cv.putText(img_copy, str(index), (x + 5, y - 5), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    #     index = index + 1

    # if index >= 4:
    #     retval, rvec, tvec = cv.solvePnP(cube_points[:index], approx.astype(np.float32), cam_matrix, dist_coeffs)
    #     distance = np.linalg.norm(tvec)
    #     text = f"Distance to camera: {distance:.2f}"
    #     text_position = (10, img.shape[0] - 10)
    #     cv.putText(img_copy, text, text_position, cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv.LINE_AA)

    # cv.imshow('approx_mask', approx_mask)
    # cv.imshow('amasked_gray', masked_gray)
    cv.imshow('mg_copy', img_copy)
    # cv.imshow('bgr_threshold', bgr_threshold)
    cv.imshow('gray', gray)

    if cv.waitKey(50) == ord('q'):
        break
cv.destroyAllWindows()
