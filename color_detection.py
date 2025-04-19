import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
from time import time
from helper_func import extract_red, extract_blue, extract_green, adjust_gamma



# vid = cv.VideoCapture("data/red vid.MOV")
loop_time = time()
frame = cv.imread("data/blue_3.jpg")

width = int(1920/2)
height = int(1080/2)
frame = cv.resize(frame, (width, height))

frame = adjust_gamma(frame, 1.5)

_, frame = extract_blue(frame)
while True:

    # FPS
    fps = 1 / (time() - loop_time)
    fps_text = f"FPS {fps: .0f}"
    cv.putText(frame, fps_text, (10, 30),
                cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    loop_time = time()

    # Show Result
    cv.imshow('Color', frame)

    # Break, stop, pause
    if cv.waitKey(50) == ord('q'):
        break
    elif cv.waitKey(50) == ord('c'):
        cv.imwrite('debug/data/{}.png' .format(loop_time), frame)
    # elif cv.waitKey(50) == ord('p'):
    #     cv.waitKey(-1)

# vid.release()
cv.destroyAllWindows