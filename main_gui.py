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
import argparse
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import sys
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton, QMainWindow
from PyQt5.QtCore import QThread, pyqtSignal

from ui_mainwindow import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self,mode=1):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


        self.ui.pushButton.clicked.connect(self.start_sorting)
        self.ui.pushButton_2.clicked.connect(self.reset_counter)

        self.red = 0
        self.green = 0
        self.blue = 0

        self.mode = mode

    def find_first_camera(self, max_test=10):
        for i in range(max_test):
            cap = cv.VideoCapture(i)
            if cap is not None and cap.isOpened():
                return cap
            cap.release()
        raise RuntimeError("No camera found")

    def start_sorting(self):
        factory = PiGPIOFactory()
        servo = Servo(12, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=factory)
        servo.value = angle_to_value(70)
        sleep(2)

        with np.load('calibration.npz') as X:
            cam_matrix, dist_coeffs = [X[i] for i in ('cam_mtx', 'dist')]

        vid = self.find_first_camera(10)
        loop_time = time()
        box = []
        zone = 0
        roi = None 
        arduino = Connector()
        if self.mode == 2:
            last_process_time = -10
            H_end_cam = Homogeous_end_to_cam()
            H_cam_obj = np.eye(4)
            H_end_obj = np.eye(4)
            trans_end_zones = np.zeros((3, 1))
        
        while True:
            # Setup frame
            ret, frame = vid.read()
            if not ret:
                print("Failed to grab frame")
                self.ui.textEdit.setText("Failed to grab frame")
                break

            # FPS
            fps = 1 / (time() - loop_time)
            fps_text = f"FPS {fps: .0f}"
            cv.putText(frame, fps_text, (10, 30),
                        cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            loop_time = time()
            current_time = time()
            elapsed_time = current_time - last_process_time

            if zone == 0:
                H_cam_obj, box = homo_matrix_from_marker(frame, cam_matrix, dist_coeffs, drawAxis=False)
                if H_cam_obj is not None and box is not None:
                    if self.mode == 2:
                        H_end_obj = H_end_cam.dot(H_cam_obj)
                        trans_end_zones = H_end_obj[:3, 3]
                        print(f"trans {trans_end_zones}") 
                    x_min, y_min, x_max, y_max = box
                    x_min = max(x_min, 0)
                    y_min = max(y_min, 0)
                    x_max = min(x_max, frame.shape[1])
                    y_max = min(y_max, frame.shape[0])
                    roi = frame[y_min-80:y_max+10, x_min-5:x_max+55]
                    zone = 1
                    print("FOUND MARKER!!!!!!!!!!!")
            if box: 
                x_min, y_min, x_max, y_max = box
                x_min = max(x_min, 0)
                y_min = max(y_min, 0)
                x_max = min(x_max, frame.shape[1])
                y_max = min(y_max, frame.shape[0])
                roi = frame[y_min-80:y_max+10, x_min-5:x_max+5]

            if zone == 1 and self.mode == 1:
                _, _ = homo_matrix_from_marker(frame, cam_matrix, dist_coeffs, drawAxis=False)
                text, percent = DetectColor(roi)
                print(text, percent)
                if text != "unknown":
                    print("GOT COLOUR!!!!!!!!!!!!!!!")
                    self.ui.textEdit.setText("GOT COLOUR!!!!!!!!!!!!!!!")
                    arduino.send_cmd("s")
                    arduino.wait_for_ready(target_message="Done!")
                    print("Grabbing!")
                    self.ui.textEdit.setText("Grabbing!")
                    servo.value = angle_to_value(0)
                    sleep(2)
                    if text == "blue":
                            arduino.send_cmd("b")
                            arduino.wait_for_ready(target_message="Sorted!")
                            self.blue += 1
                            self.ui.label_3.setText(str(self.blue))
                    elif text == "red":
                            arduino.send_cmd("r")
                            arduino.wait_for_ready(target_message="Sorted!")
                            self.red += 1
                            self.ui.label.setText(str(self.red))
                    elif text == "green":
                            arduino.send_cmd("g")
                            arduino.wait_for_ready(target_message="Sorted!")
                            self.green += 1
                            self.ui.label_2.setText(str(self.green))
                    servo.value = angle_to_value(70)
                    sleep(2)
                    arduino.wait_for_ready(target_message="Done!")
                    arduino.send_cmd("h")
                    arduino.wait_for_ready(target_message="Done!")
                    zone = 0
                
            if zone == 1 and self.mode == 2:
                if elapsed_time >= 10:
                    _, _ = homo_matrix_from_marker(frame, cam_matrix, dist_coeffs, drawAxis=False)
                    text, percent = DetectColor(roi)
                    print(text, percent)
                    if text != "unknown":
                        print("GOT COLOUR!!!!!!!!!!!!!!!")
                        self.ui.textEdit.setText("GOT COLOUR!!!!!!!!!!!!!!!")
                        x, y, z = trans_end_zones.flatten()
                        arduino.send_coords(x, y, z)
                        arduino.wait_for_ready(target_message="Done!")
                        print("Grabbing!")
                        self.ui.textEdit.setText("Grabbing!")
                        servo.value = angle_to_value(0)
                        sleep(2)
                        if text == "blue":
                            arduino.send_cmd("b")
                            arduino.wait_for_ready(target_message="Sorted!")
                            self.blue += 1
                            self.ui.label_3.setText(str(self.blue))
                        elif text == "red":
                            arduino.send_cmd("r")
                            arduino.wait_for_ready(target_message="Sorted!")
                            self.red += 1
                            self.ui.label.setText(str(self.red))
                        elif text == "green":
                            arduino.send_cmd("g")
                            arduino.wait_for_ready(target_message="Sorted!")
                            self.green += 1
                            self.ui.label_2.setText(str(self.green))
                        servo.value = angle_to_value(70)
                        sleep(2)
                        arduino.wait_for_ready(target_message="Done!")
                        arduino.send_cmd("h")
                        arduino.wait_for_ready(target_message="Done!")
                        zone = 0

                    last_process_time = current_time

            # cv.imshow('origin', frame)
            if roi is not None and roi.size > 0:
                pass
                #cv.imshow("roi", roi)
            # Break, stop, pause
            if cv.waitKey(50) == ord('q'):
                break
            elif cv.waitKey(50) == ord('c'):
                cv.imwrite('debug/data/{}.png' .format(loop_time), frame)
            elif cv.waitKey(50) == ord('g'):
                pass

        vid.release()
        cv.destroyAllWindows()

    def reset_counter(self):
        self.red = self.green = self.blue = 0
        self.ui.label.setText("0")       # đỏ
        self.ui.label_2.setText("0")     # xanh lá
        self.ui.label_3.setText("0")     # xanh dương



if __name__ == "__main__":
    app = QApplication(sys.argv)
    parser = argparse.ArgumentParser(description="Run sorting robot in different modes.")
    parser.add_argument('--mode', type=int, default=1, choices=[1,2], help='Mode 1 or Mode 2')
    args = parser.parse_args()
    window = MainWindow(mode=args.mode)
    window.show()
    sys.exit(app.exec_())
