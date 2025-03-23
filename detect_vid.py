import sys
import cv2
import numpy as np


def DetectColor(color):
    cap = cv2.VideoCapture(0)
    while True:
        _, frame = cap.read()
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
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
            break
        mask = cv2.inRange(lab, lower, upper)
        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            if cv2.contourArea(contour) > 1000:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
        cv2.imshow("mask", mask)
        cv2.imshow("video", frame)
        if cv2.waitKey(16) == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


def main():
    color = sys.argv[1]
    DetectColor(color)


if __name__ == "__main__":
    main()
