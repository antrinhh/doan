#!/usr/bin/env python3
import time
import argparse
import sys
import socket
import threading
import json
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton, QMainWindow
from PyQt5.QtCore import QThread, pyqtSignal

from ui_mainwindow import Ui_MainWindow


class MainWindow(QMainWindow):
    coordinates_signal = pyqtSignal(list)
    positions_signal = pyqtSignal(list)
    variables_signal = pyqtSignal(list)
    blue_signal = pyqtSignal(int)
    red_signal = pyqtSignal(int)
    green_signal = pyqtSignal(int)
    debug_signal = pyqtSignal(str)
    def __init__(self, port):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.logger = QTextEditLogger(self.debug_signal)
        sys.stdout = self.logger
        sys.stderr = self.logger

        self.port = port
        self.ip = self.get_local_ip()
        self.ui.pushButton.clicked.connect(self.start_sorting)
        self.ui.pushButton_2.clicked.connect(self.reset_counter)
        self.ui.reconnectButton.clicked.connect(self.connect_socket)
        
        self.ui.upxyButton_2.clicked.connect(self.controller)
        self.ui.downxyButton_2.clicked.connect(self.controller)
        self.ui.leftButton_2.clicked.connect(self.controller)
        self.ui.rightButton_2.clicked.connect(self.controller)
        self.ui.upzButton_2.clicked.connect(self.controller)
        self.ui.downzbutton_2.clicked.connect(self.controller)
        self.ui.homexyButton_2.clicked.connect(self.controller)
        self.ui.homezButton_2.clicked.connect(self.controller)

        self.coordinates_signal.connect(self.update_coordinates)
        self.positions_signal.connect(self.update_positions)
        self.variables_signal.connect(self.update_variables)
        self.blue_signal.connect(lambda v: self.ui.blue_label.setText(str(v)))
        self.red_signal.connect(lambda v: self.ui.red_label.setText(str(v)))
        self.green_signal.connect(lambda v: self.ui.green_label.setText(str(v)))
        self.debug_signal.connect(self.ui.debugTextbox.append)

        self.ui.comboBox.currentIndexChanged.connect(self.update_mode)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.mode = self.ui.comboBox.currentIndex() + 1
        self.connected = False
        self.running = False
        self.listener_thread = None
        self.red = 0
        self.green = 0
        self.blue = 0
        self.connect_socket()
        if self.connected:
            self.start_listening()

    def reset_counter(self):
        self.red = self.green = self.blue = 0
        self.ui.red_label.setText(f"{self.red}")       # Red
        self.ui.green_label.setText(f"{self.green}")     # Green
        self.ui.blue_label.setText(f"{self.blue}")     # Blue

    def update_mode(self, index):
        self.mode = index + 1
    
    def update_coordinates(self, coords):
        self.ui.x_line.setText(str(coords[0]))
        self.ui.y_line.setText(str(coords[1]))
        self.ui.z_line.setText(str(coords[2]))

    def update_positions(self, pos):
        self.ui.s1_pos_line.setText(str(pos[0]))
        self.ui.s2_pos_line.setText(str(pos[1]))
        self.ui.s3_pos_line.setText(str(pos[2]))

    def update_variables(self, vars):
        self.ui.q1_line.setText(str(vars[0]))
        self.ui.q2_line.setText(str(vars[1]))
        self.ui.q3_line.setText(str(vars[2]))
        self.ui.q4_line.setText(str(vars[3]))

    def start_sorting(self):
        start_msg = f'Start {self.mode}'
        self.socket.send((start_msg).encode())
        print(f'[SOCKET] Sent {start_msg}')
        if self.running:
                try:
                    self.socket.settimeout(1.0)  
                    ack = self.socket.recv(20)
                    if b"Got message" in ack:
                        print("[Socket] Message ACK")
                    else:
                        print(f"[Socket] Unexpected ACK: {ack}")
                except socket.timeout:
                    print("[Socket] Message NACK (timeout)")
                except Exception as e:
                    print(f"[Socket] Message NACK (error): {e}")
                finally:
                    self.socket.settimeout(None) 

    def controller(self):
        sender = self.sender()
        command = None
        if sender == self.ui.upxyButton_2:
            command = b'w'
        elif sender == self.ui.downxyButton_2:
            command = b's'
        elif sender == self.ui.leftButton_2:
            command = b'a'
        elif sender == self.ui.rightButton_2:
            command = b'd'
        elif sender == self.ui.upzButton_2:
            command = b'q'
        elif sender == self.ui.downzbutton_2:
            command = b'e'
        elif sender == self.ui.homexyButton_2 or sender == self.ui.homezButton_2:
            command = b'h'
        if command and self.connected:
            try:
                self.socket.sendall(command)
            except Exception as e:
                print(f"[Socket] Send error: {e}")
                return

            if self.running:
                try:
                    self.socket.settimeout(1.0)  # 1 second timeout for ACK
                    ack = self.socket.recv(20)
                    if b"Got message" in ack:
                        print("[Socket] Message ACK")
                    else:
                        print(f"[Socket] Unexpected ACK: {ack}")
                except socket.timeout:
                    print("[Socket] Message NACK (timeout)")
                except Exception as e:
                    print(f"[Socket] Message NACK (error): {e}")
                finally:
                    self.socket.settimeout(None)  # reset timeout

    def connect_socket(self, retries = 3):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        attemps = 0 
        while not self.connected and attemps < retries:
            try:
                self.socket.connect((self.ip, self.port))
                self.connected = True
                print(f"[Socket] Socket connected to: {self.get_local_ip()}:{self.port}\n")
            except socket.timeout:
                print("[Socket] Socket connection: timeout\n")
            except socket.gaierror:
                print("[Socket] Socket connection: gaierror\n")
            attemps = attemps + 1
            time.sleep(2)
        if not self.connected:
            print("[SOCKET] Failed to connect socket to server\n")

    def start_listening(self):
        self.running = True
        self.listener_thread = threading.Thread(target=self.listen_to_server, daemon=True).start()

    def listen_to_server(self):
        while self.running:
            try:
                data = self.socket.recv(200)
                if not data:
                    print("[SOCKET] Server disconnected\n")
                    self.running = False
                    self.connected = False
                    try:
                        self.socket.shutdown(socket.SHUT_RDWR)
                    except Exception:
                        pass
                    self.socket.close()
                msg = data.decode()
                if data:
                    print(f'[SOCKET] Message: {data.decode()}')
                    try:
                        buffer = json.loads(msg)
                        if "coordinates" in buffer and buffer["coordinates"]:
                            self.coordinates_signal.emit(buffer["coordinates"])
                        if "positions" in buffer and buffer["positions"]:
                            self.positions_signal.emit(buffer["positions"])
                        if "variables" in buffer and buffer["variables"]:
                            self.variables_signal.emit(buffer["variables"])
                        if buffer.get("Blue", 0) == 1:
                            self.blue += 1
                            self.blue_signal.emit(self.blue)
                        if buffer.get("Red", 0) == 1:
                            self.red += 1
                            self.red_signal.emit(self.red)
                        if buffer.get("Green", 0) == 1:
                            self.green += 1
                            self.green_signal.emit(self.green)
                    except Exception as e:
                        print('[SOCKET] Error getting values from server\n')
            except Exception as e:
                print(f"[SOCKET] Listening error: {e}")
                self.running = False 
                self.connected = False
                try:
                    self.socket.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                self.socket.close()
                break

    def get_local_ip(self):
        try:
            hostname = socket.gethostname()
            ip_addr = socket.gethostbyname(hostname)
            print(f'[SOCKET] Got ip addr {ip_addr}\n')
            return ip_addr
        except socket.gaierror:
            print("[SOCKET] Failed to get local ip address, will start with 127.1.0.1\n")
            ip_addr = "127.1.0.0"
            return ip_addr
        
class QTextEditLogger:
    def __init__(self, debug_signal):
        self.debug_signal = debug_signal

    def write(self, msg):
        if msg.strip():
            self.debug_signal.emit(msg.strip())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    parser = argparse.ArgumentParser(description="Run sorting robot in different modes.")
    parser.add_argument('--port', type=int, default=5000, help='Port to start listening')
    args = parser.parse_args()
    window = MainWindow(port=args.port)
    window.show()
    sys.exit(app.exec_())
