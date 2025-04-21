import cv2 as cv
import numpy as np
from helper_func import extract_blue

# filename = 'data/blue 1.jpg'
# img = cv.imread(filename)
# width = int(1920/2)
# height = int(1080/2)
# img = cv.resize(img, (width, height))
vid = cv.VideoCapture(1)
ret, img = vid.read()
dark = np.zeros(img.shape, dtype=np.uint8)
dark2 = np.zeros_like(img) 
while True:
    ret, frame = vid.read()
    # frame = cv.rotate(frame, cv.ROTATE_90_COUNTERCLOCKWISE)
    gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
    mask_blue, img_blue = extract_blue(img)
    gray_blue = cv.cvtColor(img_blue,cv.COLOR_BGR2GRAY)



    contours_blue, hierachy = cv.findContours(gray_blue, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    # cv.drawContours(dark, contours_blue, -1,  (255, 0, 0))
    for contour in contours_blue:
        eps = 0.024*cv.arcLength(contour, True)
        approx = cv.approxPolyDP(contour, eps, True)
        x, y, w, h = cv.boundingRect(contour) # feed for the tracke
        if len(approx) >= 4 and len(approx) <=10:
            cv.polylines(dark, [approx], True, (0, 0, 255), 1)
            cv.polylines(dark2, [approx], True, (0, 0, 255), 1)
            cv.polylines(frame, [approx], True, (0, 0, 255), 1)
            for i, point in enumerate(approx):
                x, y = point[0]
                cv.circle(dark2, (x, y), 3, (0, 0, 255), -1)
                cv.circle(dark, (x, y), 3, (0, 0, 255), -1)

    # cv.imshow('dark', dark)
   # Harris corner detection
    dark_gray = cv.cvtColor(dark, cv.COLOR_BGR2GRAY)
    gray_float = np.float32(dark_gray)
    dst = cv.cornerHarris(gray_float, 7, 5, 0.6)

    # Resize dst to match frame height and width if needed
    if dst.shape != frame.shape[:2]:
        dst = cv.resize(dst, (frame.shape[1], frame.shape[0]))

    corner_mask = dst > 0.04 * dst.max()
    frame[corner_mask] = [0, 0, 255]
    dark2[corner_mask] = [0, 255, 255]


    cv.imshow('gray', frame)
    cv.imshow('dst', dark2)

    if cv.waitKey(50) & 0xff == 27:
        break
vid.release()
cv.destroyAllWindows()