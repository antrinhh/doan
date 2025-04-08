import cv2 as cv
import numpy as np

def nothing(x):
    pass

cv.namedWindow('Smoothing')

cv.createTrackbar('x', 'Smoothing', 0, 10, nothing)
cv.createTrackbar('y', 'Smoothing', 0, 10, nothing)

cv.createTrackbar('minVal', 'Smoothing', 0, 255, nothing)
cv.createTrackbar('maxVal', 'Smoothing', 0, 255, nothing)

def preprocess_frame(frame):
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    # Adaptive Histogram Equalization (CLAHE)
    clahe = cv.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)

    # Reduce noise while keeping edges (Bilateral Filter)
    filtered = cv.bilateralFilter(gray, 9, 75, 75)

    # Canny Edge Detection with adaptive thresholding
    # median_val = np.median(filtered)
    # lower_thresh = int(max(0, 0.7 * median_val))
    # upper_thresh = int(min(255, 1.3 * median_val))
    # edges = cv.Canny(filtered, lower_thresh, upper_thresh)

    # # Morphological Closing to connect broken edges
    # kernel = np.ones((3, 3), np.uint8)
    # edges = cv.morphologyEx(edges, cv.MORPH_CLOSE, kernel)

    return gray


cap = cv.VideoCapture(1)

while True:
    ret, frame = cap.read()

    frame1 = preprocess_frame(frame)

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



    #canny = cv.Canny(gauss, minVal, maxVal, None, 3, 3)
    cv.imshow('origin', frame)
    cv.imshow('preprocess', frame1)
    #cv.imshow('canny', canny)
    # cv.imshow('Threshold Mask', mask)
    # cv.imshow('Dilated Mask', dilated)
    # cv.imshow('Morphological Edges', morph_edges)

    if cv.waitKey(1) & 0xFF == ord('q'):
            break
    
cap.release()
cv.destroyAllWindows