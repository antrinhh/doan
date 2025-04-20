import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
from time import time
from helper_func import extract_red, extract_blue, extract_green, adjust_gamma, mask_3_colors, morp_noise, gray_3_colors, DETECTION_RANGE_TRUE

vid = cv.VideoCapture(0)
loop_time = time()
# frame = cv.imread("data/red vid.MOV")

width = int(1920/2)
height = int(1080/2)

dark = np.zeros((height, width, 3), dtype=np.uint8)

tracker_blue = {}
tracker_red = {}
tracker_green = {}
last_process_time = -10

while True:
    ret, frame = vid.read()
    frame = cv.resize(frame, (width, height))
    frame_gamma = adjust_gamma(frame, 1.1)

    current_time = time()
    elapsed_time = current_time - last_process_time

    mask, mask_green, mask_blue, mask_red = mask_3_colors(frame_gamma)

    gray_red, gray_blue, gray_green =  gray_3_colors(frame_gamma)

    if elapsed_time >= 10:
        contours_blue, hierachy = cv.findContours(gray_blue, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        contours_green, hierachy = cv.findContours(gray_green, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        contours_red, hierachy = cv.findContours(gray_red, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        if contours_blue:
            for i, contour in enumerate(contours_blue):
                    if cv.contourArea(contour) > DETECTION_RANGE_TRUE:  
                        eps = 0.02*cv.arcLength(contour, True)
                        approx = cv.approxPolyDP(contour, eps, True)
                        tracker = cv.legacy.TrackerCSRT_create()
                        x, y, w, h = cv.boundingRect(contour) # feed for the tracker
                        tracker.init(frame, (x, y, w, h))
                        tracker_blue[f"tracker_{i}"] = tracker  
                        cv.rectangle(dark, (x, y), (x + w, y + h), (0, 255, 0), 2) 
                        if len(approx) >= 4 and len(approx) <=10:
                            cv.polylines(dark, [approx], True, (0, 0, 255), 1)
                            for i, point in enumerate(approx):
                                x, y = point[0]
                                cv.circle(dark, (x, y), 3, (0, 0, 255), -1)
        if contours_red:
            for i, contour in enumerate(contours_red):
                    if cv.contourArea(contour) > DETECTION_RANGE_TRUE:  
                        eps = 0.02*cv.arcLength(contour, True)
                        approx = cv.approxPolyDP(contour, eps, True)
                        tracker = cv.legacy.TrackerCSRT_create()
                        x, y, w, h = cv.boundingRect(contour) # feed for the tracker
                        tracker.init(frame, (x, y, w, h))
                        tracker_red[f"tracker_{i}"] = tracker  
                    #     cv.rectangle(dark, (x, y), (x + w, y + h), (0, 255, 0), 2) 
                    #     if len(approx) >= 4 and len(approx) <=10:
                    #         cv.polylines(dark, [approx], True, (0, 0, 255), 1)
                    #         for i, point in enumerate(approx):
                    #             x, y = point[0]
                    #             cv.circle(dark, (x, y), 3, (0, 0, 255), -1)
        if contours_green:
            for i, contour in enumerate(contours_green):
                    if cv.contourArea(contour) > DETECTION_RANGE_TRUE:  
                        eps = 0.02*cv.arcLength(contour, True)
                        approx = cv.approxPolyDP(contour, eps, True)
                        tracker = cv.legacy.TrackerCSRT_create()
                        x, y, w, h = cv.boundingRect(contour) # feed for the tracker
                        tracker.init(frame, (x, y, w, h))
                        tracker_green[f"tracker_{i}"] = tracker  
                    #     cv.rectangle(dark, (x, y), (x + w, y + h), (0, 255, 0), 2) 
                    #     if len(approx) >= 4 and len(approx) <=10:
                    #         cv.polylines(dark, [approx], True, (0, 0, 255), 1)
                    #         for i, point in enumerate(approx):
                    #             x, y = point[0]
                    #             cv.circle(dark, (x, y), 3, (0, 0, 255), -1)        
        last_process_time = current_time

    for key, tracker in tracker_blue.items():
        success, box = tracker.update(frame)
        if success:
            x, y, w, h = map(int, box)
            cv.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv.putText(frame, key, (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

    for key, tracker in tracker_red.items():
        success, box = tracker.update(frame)
        if success:
            x, y, w, h = map(int, box)
            cv.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv.putText(frame, key, (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    for key, tracker in tracker_green.items():
        success, box = tracker.update(frame)
        if success:
            x, y, w, h = map(int, box)
            cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv.putText(frame, key, (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    # FPS
    # fps = 1 / (time() - loop_time)
    # fps_text = f"FPS {fps: .0f}"
    # cv.putText(frame, fps_text, (10, 30),
    #             cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    # loop_time = time()
    

    # Show Result
    cv.imshow('result', frame)
    cv.imshow('red', gray_red)
    # Break, stop, pause
    if cv.waitKey(50) == ord('q'):
        break
    elif cv.waitKey(50) == ord('c'):
        cv.imwrite('debug/data/{}.png' .format(loop_time), frame)
    # elif cv.waitKey(50) == ord('p'):
    #     cv.waitKey(-1)

vid.release()
cv.destroyAllWindows