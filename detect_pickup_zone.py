import cv2 as cv
import numpy as np
from helper_func import adjust_gamma


def arm_scan():
    return True

def detect_pickup_zone(frame):
    while arm_scan()==True: #Arm scanning with a fix posiotion from angle start to finish
        frame = adjust_gamma(frame, 0.8)
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        mask = cv.inRange(gray, 20, 200)
        contours, hierarchy = cv.findContours(mask, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
        approx_contours = [] 
        if contours and len(contours) >= 2:
            for cnt in contours:
                esp = 0.02 * cv.arcLength(cnt, True)
                approx = cv.approxPolyDP(cnt, esp, True)
                if len(approx) == 4:
                    approx_contours.append(approx)
                    cv.polylines(frame, [approx], True, (250, 120, 200), 3)

    return tuple(approx_contours)

def main():
    vid = cv.VideoCapture(1)
    while True:
        ret, frame = vid.read()
        
        frame = cv.rotate(frame, cv.ROTATE_90_COUNTERCLOCKWISE)
        zones = detect_pickup_zone(frame)

        cv.drawContours(frame, zones, -1,  (250, 250, 250), 3)

        cv.imshow("Pickup Zone Detection", frame)
        if cv.waitKey(50) == ord('q'):
            break
        # elif cv.waitKey(50) == ord('p'):
        #     cv.waitKey(-1)
    vid.release()
    cv.destroyAllWindows

if __name__ == '__main__':
    main()