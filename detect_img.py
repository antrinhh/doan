import cv2
import sys
import numpy as np


def DetectColor(image, color):
    img = image
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    if color == 'red':
        lower = np.array([20, 140, 120])
        upper = np.array([255, 230, 238])
    elif color == 'green':
        lower = np.array([50, 0, 134])
        upper = np.array([255, 255, 255])
    elif color == 'blue':
        lower = np.array([0, 118, 70])
        upper = np.array([188, 255, 117])
    else:
        print("Error")
    mask = cv2.inRange(lab, lower, upper)
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        if cv2.contourArea(contour) > 1000:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
    cv2.imshow("mask", mask)
    cv2.imshow("image", img)
    if cv2.waitKey(0) == ord('q'):
        cv2.destroyAllWindows()


def main():
    img = cv2.imread("red1.jpg")
    img = cv2.resize(img, (640, 480))
    color = sys.argv[1]
    DetectColor(img, color)


if __name__ == "__main__":
    main()
