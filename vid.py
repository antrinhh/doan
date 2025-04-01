import cv2 as cv
import numpy as np

def nothing(x):
    pass

cv.namedWindow('Smoothing')

cv.createTrackbar('x', 'Smoothing', 0, 10, nothing)
cv.createTrackbar('y', 'Smoothing', 0, 10, nothing)

cv.createTrackbar('minVal', 'Smoothing', 0, 255, nothing)
cv.createTrackbar('maxVal', 'Smoothing', 0, 255, nothing)
cap = cv.VideoCapture(1)

while True:
    ret, frame = cap.read()

    frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    _, mask = cv.threshold(frame, 100, 255, cv.THRESH_BINARY)

    # Dilate the mask
    kernel = np.ones((3, 3), np.uint8)
    dilated = cv.dilate(mask, kernel, iterations=1)

    # Compute absolute difference (Dilated - Original Mask)
    morph_edges = cv.absdiff(dilated, mask)

    # Invert polarity (Make edges white on black background)
    morph_edges = cv.bitwise_not(morph_edges)


    x = cv.getTrackbarPos('x', 'Smoothing')
    y = cv.getTrackbarPos('y', 'Smoothing')
    gauss = cv.GaussianBlur(frame, (9, 9), x, y)
    
    minVal = cv.getTrackbarPos('minVal', 'Smoothing')
    maxVal = cv.getTrackbarPos('maxVal', 'Smoothing')

    canny = cv.Canny(gauss, minVal, maxVal, None, 3, 3)
    cv.imshow('origin', gauss)
    cv.imshow('canny', canny)
    cv.imshow('Threshold Mask', mask)
    cv.imshow('Dilated Mask', dilated)
    cv.imshow('Morphological Edges', morph_edges)

    if cv.waitKey(1) & 0xFF == ord('q'):
            break
    
cap.release()
cv.destroyAllWindows