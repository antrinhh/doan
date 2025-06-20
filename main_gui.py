#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton, QMainWindow
from PyQt5.QtCore import QThread, pyqtSignal

from worker_gui import DetectionWorker
from ui_mainwindow import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.thread = DetectionWorker()
        self.thread.color_detected.connect(self.update_label)

        self.ui.pushButton.clicked.connect(self.start_sorting)
        self.ui.pushButton_2.clicked.connect(self.reset_counter)

        self.red = 0
        self.green = 0
        self.blue = 0

    def start_sorting(self):
        self.thread.start()

    def reset_counter(self):
        self.red = self.green = self.blue = 0
        self.ui.label.setText("0")       # đỏ
        self.ui.label_2.setText("0")     # xanh lá
        self.ui.label_3.setText("0")     # xanh dương

    def update_label(self, color, count):
        if color == "red":
            self.red += 1
            self.ui.label.setText(str(count))
        elif color == "green":
            self.green += 1
            self.ui.label_2.setText(str(count))
        elif color == "blue":
            self.blue += 1
            self.ui.label_3.setText(str(count))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
