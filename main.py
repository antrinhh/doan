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
import sys
import socket
import threading
import json

global is_free
is_free = True

def find_first_camera(max_test=10):
    for i in range(max_test):
        cap = cv.VideoCapture(i)
        if cap is not None and cap.isOpened():
            return cap
        cap.release()
    raise RuntimeError("No camera found")

def get_local_ip():
    try:
        hostname = socket.gethostname()
        ip_addr = socket.gethostbyname(hostname)
        print(f'[SOCKET] local ip addr grabbed {ip_addr}')
        return ip_addr
    except socket.gaierror:
        print("[SOCKET] Failed to get local ip address, will start with 127.1.0.1")
        ip_addr = "127.1.0.0"
        return ip_addr

def socket_init(port):
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = get_local_ip()
    soc.bind((host, port))
    soc.listen(1)
    print(f"[SOCKET] Starting on: {host}:{port}")
    conn, addr = soc.accept()
    while conn:
        print("[SOCKET] Connected by:", addr)
        return conn

def socket_recv(conn, start_event, mode_flag, move_flag):
    try: 
        while True:
            ack_needed = False
            data = conn.recv(20)
            msg = data.decode().strip()
            if 'Start 1' in msg:
                mode_flag['value'] = 1
                start_event.set()
                ack_needed = True
            elif 'Start 2' in msg:
                mode_flag['value'] = 2
                start_event.set()
                ack_needed = True
            
            if is_free:
                if 'w' in msg:
                    move_flag['value'] = 1
                    ack_needed = True
                elif 'a' in msg:
                    move_flag['value'] = 2
                    ack_needed = True
                elif 's' in msg:
                    move_flag['value'] = 3
                    ack_needed = True
                elif 'd' in msg:
                    move_flag['value'] = 4
                    ack_needed = True
                elif 'q' in msg:
                    move_flag['value'] = 5
                    ack_needed = True
                elif 'e' in msg:
                    move_flag['value'] = 6
                    ack_needed = True
                elif 'h' in msg:
                    move_flag['value'] = 7
                    ack_needed = True
                else:
                    print(f"[SOCKET] Unknown: {msg}")
            if ack_needed:
                try:
                    conn.sendall(b"Got message\n")
                except Exception as e:
                    print(f"[SOCKET] Failed to send ACK: {e}")
                    break
    except Exception as e:
        print(f"[SOCKET] Error: {e}")

def main(conn, mode=1, show=False):    
    factory = PiGPIOFactory()
    servo = Servo(18, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=factory)
    servo.value = angle_to_value(70)
    sleep(2)

    with np.load('/home/siuw/Documents/doan/calibration.npz') as X:
        cam_matrix, dist_coeffs = [X[i] for i in ('cam_mtx', 'dist')]
    vid = find_first_camera()
    if not vid.isOpened():
        sys.exit(1)
    # loop_time = time()
    box = []
    zone = 0
    roi = None 
    arduino = Connector()
    arduino.set_conn(conn)
    if mode == 2:
        last_process_time = -10
        H_end_cam = Homogeous_end_to_cam()
        H_cam_obj = np.eye(4)
        H_end_obj = np.eye(4)
        trans_end_zones = np.zeros((3, 1))
    if show == True:
        cv.namedWindow("Frame", cv.WINDOW_NORMAL)
        cv.resizeWindow("Frame", 800, 480)
    print('[MAIN] Starting')
    while True:
        # Setup frame
        ret, frame = vid.read()
        if not ret:
            print("Failed to grab frame")
            break
        # loop_time = time()
        # current_time = time()
        # if mode == 2:
        #     elapsed_time = current_time - last_process_time
        print('[MAIN] InLoop')
        if zone == 0:
            H_cam_obj, box = homo_matrix_from_marker(frame, cam_matrix, dist_coeffs, drawAxis=False)
            print(f"[DEBUG] Marker detection: H={H_cam_obj is not None}, box={box}")
            if H_cam_obj is not None and box is not None:
                if mode == 2:
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
        print('[MAIN] InLoop 2')
        # print(f'box: {box}')
        if box: 
            x_min, y_min, x_max, y_max = box
            x_min = max(x_min, 0)
            y_min = max(y_min, 0)
            x_max = min(x_max, frame.shape[1])
            y_max = min(y_max, frame.shape[0])
            roi = frame[y_min-80:y_max+10, x_min-5:x_max+5]

        if zone == 1 and mode == 1 and roi is not None and roi.size > 0:            
            # _, _ = homo_matrix_from_marker(frame, cam_matrix, dist_coeffs, drawAxis=False)
            text, percent = DetectColor(roi)
            print(text, percent)
            if text != "unknown":
                is_free = False
                print("GOT COLOUR!!!!!!!!!!!!!!!")
                arduino.send_cmd("u")
                arduino.wait_for_ready(target_message="Done!")
                print("Grabbing!")
                servo.value = angle_to_value(0)
                sleep(2)
                if text == "blue":
                    arduino.send_cmd("b")
                    arduino.wait_for_ready(target_message=" Blue Sorted!")

                elif text == "red":
                    arduino.send_cmd("r")
                    arduino.wait_for_ready(target_message="Red Sorted!")

                elif text == "green":
                    arduino.send_cmd("g")
                    arduino.wait_for_ready(target_message="Green Sorted!")

                servo.value = angle_to_value(70)
                sleep(2)
                arduino.wait_for_ready(target_message="Done!")
                arduino.send_cmd("h")
                arduino.wait_for_ready(target_message="Done!")
                zone = 0
                is_free = True
        print("[MAIN] Inloop3")
        if zone == 1 and mode == 2 and roi is not None and roi.size > 0:
            # if elapsed_time >= 10:
            # _, _ = homo_matrix_from_marker(frame, cam_matrix, dist_coeffs, drawAxis=False)
            text, percent = DetectColor(roi)
            print(text, percent)
            if text != "unknown":
                is_free = False
                print("GOT COLOUR!!!!!!!!!!!!!!!")
                x, y, z = trans_end_zones.flatten()
                arduino.send_coords(x, y, z)
                arduino.wait_for_ready(target_message="Done!")
                print("Grabbing!")
                servo.value = angle_to_value(13)
                sleep(2)
                if text == "blue":
                    arduino.send_cmd("b")
                    arduino.wait_for_ready(target_message="Sorted!")
                   
                elif text == "red":
                    arduino.send_cmd("r")
                    arduino.wait_for_ready(target_message="Sorted!")
                    
                elif text == "green":
                    arduino.send_cmd("g")
                    arduino.wait_for_ready(target_message="Sorted!")
                   
                servo.value = angle_to_value(70)
                sleep(2)
                arduino.wait_for_ready(target_message="Done!")
                arduino.send_cmd("h")
                arduino.wait_for_ready(target_message="Done!")
                zone = 0
                is_free = True

                # last_process_time = current_time

        # # Break, stop, pause
        key = cv.waitKey(1) & 0xFF
        if key == ord('q'):
            print("[MAIN] Quit pressed.")
            break
        elif key == ord('c'):
            pass
        elif key == ord('g'):
            pass
        elif key == ord('y'):
            pass
            # arduino.send_cmd("y")

    vid.release()
    cv.destroyAllWindows()
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run sorting robot in different modes.")
    parser.add_argument('--port', type=int , default=5000,  help='Choose port for socket server')
    parser.add_argument('--show', action='store_true', help='Want to show frame or not?')
    args = parser.parse_args()
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = get_local_ip()
    soc.bind((host, args.port))
    soc.listen(1)
    print(f"[SOCKET] Starting on: {host}:{args.port}")
    while True:
        conn, addr = soc.accept()
        print("[SOCKET] Connected by:", addr)

        start_event = threading.Event()
        mode_flag = {'value': 0}
        move_flag = {'value': 0}

        threading.Thread(target=socket_recv, args=(conn, start_event, mode_flag, move_flag), daemon=True).start()

        print('[MAIN] Waiting for start event')

        print("[MAIN] Waiting for start event (max 10s)...")
        start_time = time()
        while not start_event.is_set():
            if time() - start_time > 30:
                print("[MAIN] Timeout waiting for start event\n")
                try:
                    conn.shutdown(socket.SHUT_RDWR)
                except:
                    pass
                conn.close()
                break  # to accept()
            sleep(0.1)

        if not start_event.is_set():
            continue  
        try:
            main(conn, mode=mode_flag['value'], show=args.show)
        except Exception as e:
            print(f'[MAIN] Error {e}')
        finally:
            try:
                conn.shutdown(socket.SHUT_RDWR)
            except:
                pass
            conn.close()
            print('[MAIN] Client disconnected. Restarting...\n')
