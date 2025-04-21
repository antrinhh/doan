import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
from time import time
from helper_func import extract_red, extract_blue, extract_green, adjust_gamma, mask_3_colors, morp_noise, gray_3_colors
from cube_class import Cube_2

DETECTION_RANGE_TRUE = 5000


vid = cv.VideoCapture(1)
loop_time = time()
# frame = cv.imread("data/red vid.MOV")

# width = int(1920/2)
# height = int(1080/2)

tracker_blue = {}
tracker_red = {}
tracker_green = {}
last_process_time = -10
trackers = {}
cube = {}
count_object = 0

# fourcc = cv.VideoWriter_fourcc(*'XVID')  # You can also use 'MJPG' or 'MP4V'
# out = cv.VideoWriter('data/output/output.avi', fourcc, 20.0, (width, height))  # 20 FPS
while True:
    ret, frame = vid.read()
    frame = cv.rotate(frame, cv.ROTATE_90_COUNTERCLOCKWISE)
    # frame = cv.resize(frame)
    frame = adjust_gamma(frame, 1.5)
    frame = cv.medianBlur(frame, 5)

    current_time = time()
    elapsed_time = current_time - last_process_time

    # FPS
    fps = 1 / (time() - loop_time)
    fps_text = f"FPS {fps: .0f}"
    cv.putText(frame, fps_text, (10, 30),
                cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    loop_time = time()
    
    mask, mask_green, mask_blue, mask_red = mask_3_colors(frame)

    gray_red, gray_blue, gray_green =  gray_3_colors(frame)

    if elapsed_time >= 10:
        count_object = 0
        tracker_green.clear()
        tracker_red.clear()
        tracker_blue.clear()
        contours_blue, hierachy = cv.findContours(gray_blue, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        contours_green, hierachy = cv.findContours(gray_green, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        contours_red, hierachy = cv.findContours(gray_red, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

      
        # if contours:
        #     for i, contour in enumerate(contours):
        #          if cv.contourArea(contour) > DETECTION_RANGE_TRUE:
        #             x, y, w, h = cv.boundingRect(contour)  
        #             trackers.init(frame, (x, y, w, h))
        #             trackers[f"tracker_{i}"] = tracker

        # for key, tracker in trackers.items():
        #     success, box = tracker.update(frame)
        #     if success:
        #         x, y, w, h = map(int, box)
        #         cv.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        #         cv.putText(frame, key, (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

        if contours_blue:
            for i, contour in enumerate(contours_blue):
                    if cv.contourArea(contour) > DETECTION_RANGE_TRUE:  
                        tracker = cv.legacy.TrackerCSRT_create()
                        x, y, w, h = cv.boundingRect(contour) # feed for the tracker
                        tracker.init(frame, (x, y, w, h))
                        tracker_blue[f"Cube_{count_object}"] = tracker
                        cube[f"Cube_{count_object}"] = Cube_2(f"Cube_{count_object}", frame, 'blue', (x, y, w, h), contour, save_flag=True)

        if contours_red:
            for i, contour in enumerate(contours_red):
                    if cv.contourArea(contour) > DETECTION_RANGE_TRUE:  
                        tracker = cv.legacy.TrackerCSRT_create()
                        x, y, w, h = cv.boundingRect(contour) # feed for the tracker
                        tracker.init(frame, (x, y, w, h))
                        tracker_red[f"Cube_{i}"] = tracker  
                        cube[f"Cube_{count_object}"] = Cube_2(f"Cube_{count_object}", frame, 'red', (x, y, w, h), contour)

        if contours_green:
            for i, contour in enumerate(contours_green):
                    if cv.contourArea(contour) > DETECTION_RANGE_TRUE:  
                        tracker = cv.legacy.TrackerCSRT_create()
                        x, y, w, h = cv.boundingRect(contour) # feed for the tracker
                        tracker.init(frame, (x, y, w, h))
                        tracker_green[f"Cube_{i}"] = tracker  
                        cube[f"Cube_{count_object}"] = Cube_2(f"Cube_{count_object}", frame, 'green', (x, y, w, h), contour) 
                                
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


    # Show Result
    cv.imshow('result', frame)
    cv.imshow('mask', mask_blue)
    # Break, stop, pauseq
    if cv.waitKey(50) == ord('q'):
        break
    elif cv.waitKey(50) == ord('c'):
        cv.imwrite('debug/data/{}.png' .format(loop_time), frame)
    # elif cv.waitKey(50) == ord('p'):
    #     cv.waitKey(-1)

vid.release()
# out.release()
cv.destroyAllWindows