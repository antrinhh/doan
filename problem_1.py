import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
from time import time
from helper_func import extract_red, extract_blue, extract_green, adjust_gamma, mask_3_colors, morp_noise, gray_3_colors, is_closed_contour, load_calibration
from connector import Connector
from detect_pickup_zone import detect_pickup_zone, distance_to_zone, DetectColor, ZONE_DIMENSION
from matrixes import Homogeous_end_to_cam, get_homogeous_matrix

def main():
    cam_matrix, dist_coeffs = load_calibration()
    print(cam_matrix)
    vid = cv.VideoCapture(1)
    loop_time = time()
    # arduino = Connector()
    last_process_time = -10
    H_end_cam = Homogeous_end_to_cam()
    H_cam_obj = np.eye(4)
    H_end_obj = np.eye(4)
    trans_end_zones = np.zeros((3, 1))
    box = []
    zone = 0 
    roi = mask = None
    arduino = Connector()
    while True:
        # Setup frame
        ret, frame = vid.read()
        if not ret:
            print("Failed to grab frame")
            break
        frame = cv.rotate(frame, cv.ROTATE_90_COUNTERCLOCKWISE)
        # frame = cv.resize(frame)
        frame = adjust_gamma(frame, 1.1)
        copy = frame.copy()
        
        # FPS
        fps = 1 / (time() - loop_time)
        fps_text = f"FPS {fps: .0f}"
        cv.putText(frame, fps_text, (10, 30),
                    cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        loop_time = time()

        if box: 
            x, y, w, h = box
            pt1 = (max(x - 100, 0), max(y - 100, 0))
            pt2 = (min(x + w + 100, frame.shape[1]), min(y + h + 100, frame.shape[0]))
            cv.rectangle(frame, pt1, pt2, (0, 255, 0), 2)

            # Extract ROI
            roi = frame[pt1[1]:pt2[1], pt1[0]:pt2[0]]

        current_time = time()
        elapsed_time = current_time - last_process_time
        if zone == 0:
            points, box, mask = detect_pickup_zone(frame)
            points = np.array(points, dtype=np.float32)
            retval, rvec, tvec = distance_to_zone(points, cam_matrix, dist_coeffs)
            if retval:
                H_cam_obj = get_homogeous_matrix(rvec, tvec)
                H_end_obj = H_end_cam.dot(H_cam_obj)
                trans_end_zones = H_end_obj[:3, 3]
                zone += 1
                print(f"trans {trans_end_zones}")
        else:
            _, _, mask = detect_pickup_zone(frame)

        if elapsed_time >= 10:
            if zone == 1:
                if roi is not None and roi.size != 0:
                    text, _ = DetectColor(roi)
                    if text != "unknown":
                        x, y, z = trans_end_zones.flatten()
                        if text == "red":
                            arduino.send_command(x, y, z, 1, 1)
                        elif text == "blue":
                            arduino.send_command(x, y, z, 1, 2)
                        elif text == "green":
                            arduino.send_command(x, y, z, 1, 3)
            
                
            last_process_time = current_time


        cv.imshow('origin', frame)
        cv.imshow('mask', mask)
        if roi is not None and roi.size != 0:
            cv.imshow("ROI", roi)
        # Break, stop, pause
        if cv.waitKey(50) == ord('q'):
            break
        elif cv.waitKey(50) == ord('c'):
            cv.imwrite('debug/data/{}.png' .format(loop_time), frame)
        elif cv.waitKey(50) == ord('g'):
            pass
        # elif cv.waitKey(50) == ord('p'):
        #     cv.waitKey(-1)
    vid.release()
    # out.release()
    cv.destroyAllWindows

if __name__ == "__main__":
    main()