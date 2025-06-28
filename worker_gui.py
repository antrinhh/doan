#!/usr/bin/env python3
from gpiozero import Servo
from time import sleep
from gpiozero.pins.pigpio import PiGPIOFactory
from time import time
from connector import Connector
from detect_pickup_zone import DetectColor
from aruco_detect import homo_matrix_from_marker
from helper_func import angle_to_value
from matrixes import Homogeous_end_to_cam
import threading
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtCore import QThread, pyqtSignal


class DetectionWorker(QThread):
    color_detected = pyqtSignal(str)
    show_frame = pyqtSignal(np.ndarray)
    log_signal = pyqtSignal(str)

    def find_first_camera(max_test=10):
        for i in range(max_test):
            cap = cv.VideoCapture(i)
            if cap is not None and cap.isOpened():
                return cap
            cap.release()
        raise RuntimeError("No camera found")

    def __init__(self, mode=1):
        super().__init__()
        self.mode = mode
        self.running = False
        with np.load('/home/siuw/Documents/doan/calibration.npz') as X:
            self.cam_matrix, self.dist_coeffs = [X[i] for i in ('cam_mtx', 'dist')]
        self.servo = Servo(18, min_pulse_width=0.5/1000,
                      max_pulse_width=2.5/1000, pin_factory=PiGPIOFactory())
        self.arduino = Connector()
        self.vid = self.find_first_camera()
        self.box = []
        self.zone = 0
        self.roi = None
        if self.mode == 2:
            self.last_process_time = -10
            self.H_end_cam = Homogeous_end_to_cam()
            self.H_cam_obj = np.eye(4)
            self.H_end_obj = np.eye(4)
            self.trans_end_zones = np.zeros((3, 1))

    def start(self):
        self.running = True
        self.servo.value = angle_to_value(70)
        sleep(2)
        self.thread = threading.Thread(target=self.loop)
        self.thread.start()

    def stop(self):
        self.running = False
        self.vid.release()
        cv.destroyAllWindows()

    def loop(self):
        while self.running:
            # Setup frame
            ret, frame = self.vid.read()
            if not ret:
                print("Failed to grab frame")
                break

            # FPS
            fps = 1 / (time() - loop_time)
            fps_text = f"FPS {fps: .0f}"
            cv.putText(frame, fps_text, (10, 30),
                       cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            loop_time = time()
            current_time = time()
            if self.mode == 2:
                elapsed_time = current_time - self.last_process_time

            if self.zone == 0:
                if self.mode == 1:
                    _, self.box = homo_matrix_from_marker(frame, self.cam_matrix, self.dist_coeffs, drawAxis=False)
                else:
                    self.H_cam_obj, self.box = homo_matrix_from_marker(frame, self.cam_matrix, self.dist_coeffs, drawAxis=False)
                if self.box is not None and (self.mode == 1 or self.H_cam_obj is not None):
                    if self.mode == 2:
                        self.H_end_obj = self.H_end_cam.dot(self.H_cam_obj)
                        self.trans_end_zones = self.H_end_obj[:3, 3]
                        print(f"trans {self.trans_end_zones}") 
                    x_min, y_min, x_max, y_max = self.box
                    x_min = max(x_min, 0)
                    y_min = max(y_min, 0)
                    x_max = min(x_max, frame.shape[1])
                    y_max = min(y_max, frame.shape[0])
                    self.roi = frame[y_min-80:y_max+10, x_min-5:x_max+55]
                    self.zone = 1
                    print("FOUND MARKER!!!!!!!!!!!")
            if self.box: 
                x_min, y_min, x_max, y_max = self.box
                x_min = max(x_min, 0)
                y_min = max(y_min, 0)
                x_max = min(x_max, frame.shape[1])
                y_max = min(y_max, frame.shape[0])
                roi = frame[y_min-80:y_max+10, x_min-5:x_max+5]

            if zone == 1 and self.mode == 1:
                _, _ = homo_matrix_from_marker(frame, self.cam_matrix, self.dist_coeffs, drawAxis=False)
                text, percent = DetectColor(roi)
                print(text, percent)
                if text != "unknown":
                    print("GOT COLOUR!!!!!!!!!!!!!!!")
                    self.arduino.send_cmd("s")
                    self.arduino.wait_for_ready(target_message="Done!")
                    print("Grabbing!")
                    self.servo.value = angle_to_value(0)
                    sleep(2)
                    if text == "blue":
                        self.arduino.send_cmd("b")
                        self.arduino.wait_for_ready(target_message="Sorted!")
                    elif text == "red":
                        self.arduino.send_cmd("r")
                        self.arduino.wait_for_ready(target_message="Sorted!")
                    elif text == "green":
                        self.arduino.send_cmd("g")
                        self.arduino.wait_for_ready(target_message="Sorted!")
                    self.servo.value = angle_to_value(70)
                    sleep(2)
                    self.arduino.wait_for_ready(target_message="Done!")
                    self.arduino.wait_for_ready(target_message="Done!")
                    zone = 0
                
            if zone == 1 and self.mode == 2:
                if elapsed_time >= 10:
                    _, _ = homo_matrix_from_marker(frame, self.cam_matrix, self.dist_coeffs, drawAxis=False)
                text, percent = DetectColor(roi)
                print(text, percent)
                if text != "unknown":
                    print("GOT COLOUR!!!!!!!!!!!!!!!")
                    x, y, z = self.trans_end_zones.flatten()
                    self.arduino.send_coords(x, y, z)
                    self.arduino.wait_for_ready(target_message="Done!")
                    print("Grabbing!")
                    self.servo.value = angle_to_value(0)
                    sleep(2)
                    if text == "blue":
                        self.arduino.send_cmd("b")
                        self.arduino.wait_for_ready(target_message="Sorted!")
                    elif text == "red":
                        self.arduino.send_cmd("r")
                        self.arduino.wait_for_ready(target_message="Sorted!")
                    elif text == "green":
                        self.arduino.send_cmd("g")
                        self.arduino.wait_for_ready(target_message="Sorted!")
                    self.servo.value = angle_to_value(70)
                    sleep(2)
                    self.arduino.wait_for_ready(target_message="Done!")
                    self.arduino.send_cmd("h")
                    self.arduino.wait_for_ready(target_message="Done!")
                    zone = 0

                    self.last_process_time = current_time

            # cv.imshow('origin', frame)
            # if roi is not None and roi.size > 0:
                pass
                # cv.imshow("roi", roi)
            # Break, stop, pause
            if cv.waitKey(50) == ord('q'):
                break
            elif cv.waitKey(50) == ord('c'):
                cv.imwrite('debug/data/{}.png' .format(loop_time), frame)
            elif cv.waitKey(50) == ord('g'):
                pass

        

