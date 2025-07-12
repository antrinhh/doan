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
from worker_gui import DetectionWorker
from ui_mainwindow import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self,mode=1):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.controller = DetectionWorker(mode=mode)

        self.ui.pushButton.clicked.connect(self.controller.start)
        self.ui.pushButton_2.clicked.connect(self.controller.stop)
        self.ui.pushButton_2.click.connect(self.reset_counter)

        self.red = 0
        self.green = 0
        self.blue = 0

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
