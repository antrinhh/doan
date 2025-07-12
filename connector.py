import serial
import time
import threading
import serial.tools.list_ports
import re
import json


class Connector:
    def __init__(self, baudrate=9600, timeout=1, listen_flag = 1):
        self.port = self.find_arduino()
        self.baudrate = baudrate
        self.timeout = timeout
        self.arduino = None
        self.parity = serial.PARITY_NONE
        self.stopbits = serial.STOPBITS_ONE
        self.bytesize = serial.EIGHTBITS
        self.running = False
        self.conn_lock = threading.Lock()
        self.connect_arduino()
        if self.arduino and listen_flag:
            print("[CONNECTOR] Arduino connected")
            self.start_listening()
        
    def connect_arduino(self, retries=5):
        attempts = 0
        while not self.arduino and attempts < retries:
            try:
                self.arduino = serial.Serial(self.port, self.baudrate, parity=self.parity, stopbits=self.stopbits, bytesize=self.bytesize, timeout=self.timeout)
                time.sleep(2)  
                self.send_cmd("i")
                if self.wait_for_ready():
                    return
                else:
                    self.arduino.close()
                    self.arduino = None
                    return
            except Exception as e:
                print(f"[CONNECTOR] Connection attempt {attempts+1} failed: {e}")
                attempts += 1
                time.sleep(1)
        if not self.arduino:
            print("[CONNECTOR] Failed to connect to Arduino after multiple attempts.")

    def set_conn(self, conn):
        self.conn = conn
    
    def send_cmd(self, cmd):
        if cmd is None:
            print("[CONNECTOR] Cannot send command, no color is detected")
            return
        if self.arduino and self.arduino.is_open:
            command = f"{cmd}\n"
            self.arduino.write(command.encode())
            print(f"[CONNECTOR] Sent: {command.strip()}")
        else:
            print("[CONNECTOR] Arduino not connected")
    
    def send_coords(self, x, y, z):
        if None in [x, y, z]:
            print("[CONNECTOR] Cannot send command. One or more coordinates are None.")
            return
        
        if self.arduino and self.arduino.is_open:
            command = f"{x:.2f},{y:.2f},{z:.2f}\n"  # Command format
            self.arduino.write(command.encode())
            print(f"[CONNECTO] Sent: {command.strip()}")
        else:
            print("[CONNECTOR] Arduino is not connected")

    def wait_for_ready(self, target_message="Finish setup", timeout=100):
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                if self.arduino and self.arduino.in_waiting > 0:
                    line = self.arduino.readline().decode('utf-8', errors='ignore').strip()
                    if target_message in line:
                        print(f"[CONNECTOR]: {target_message}")
                        return True
            except Exception as e:
                print(f"[CONNECTOR] {e}")
                return False
        print(f"[CONNECTER] Timeout waiting for '{target_message}'")
        return False
    
    def start_listening(self):
        self.running = True
        self.listener_thread = threading.Thread(target=self.listen_to_arduino, daemon=True)
        self.listener_thread.start()
        
    def stop(self):
        self.running = False
        if self.arduino and self.arduino.is_open:
            self.arduino.close()
        print("[CONNECTOR] Stopped connection.")

    def find_arduino(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if ('Arduino' in port.description or 
                'CH340' in port.description or
                'CP210' in port.description or
                'USB Serial' in port.description):
                return port.device
        return '/dev/ttyAMA0'

    def reconnect(self):
        print("[CONNECTOR] Reconnecting to Arduino...")
        self.stop()
        self.port = self.find_arduino()
        self.connect_arduino()
        if self.arduino:
            self.start_listening()
    
    def listen_to_arduino(self):
        buffer_pos = {"coordinates": None, "positions": None, "variables": None}
        buffer_color = {"blue": 0, "red": 0, "green": 0}
        while self.running:
            updated_pos = False
            updated_color = False
            try:
                if self.arduino and self.arduino.in_waiting > 0:
                    line = self.arduino.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        print(f"[CONNECTOR] {line}")
                        if line.startswith("Coordinates:"):
                            coords = line.replace("Coordinates:", "").strip()
                            buffer_pos["coordinates"] = [float(x) for x in coords.split(",")]
                            updated_pos = True
                        elif line.startswith("Positions:"):
                            positions = line.replace("Positions:", "").strip()
                            buffer_pos["positions"] = [float(x) for x in positions.split(",")]
                            updated_pos = True
                        elif line.startswith("Variables:"):
                            variables = line.replace("Variables:", "").strip()
                            buffer_pos["variables"] = [float(x) for x in variables.split(",")]
                            updated_pos = True
                        elif "Blue Sorted!" in line:
                            buffer_color["blue"] = 1
                            updated_color = True
                        elif "Red Sorted!" in line:
                            buffer_color["red"] = 1
                            updated_color = True
                        elif "Green Sorted!" in line:
                            buffer_color["green"] = 1
                            updated_color = True
                        if self.conn and updated_pos:
                            try:
                                msg_to_send = json.dumps(buffer_pos)
                                with self.conn_lock:
                                    self.conn.sendall((msg_to_send + "\n").encode())
                            except Exception as e:
                                print(f"[CONNECTOR] Failed to send to GUI: {e}")
                                self.conn = None
                        if self.conn and updated_color:
                            try:
                                msg_to_send = json.dumps(buffer_color)
                                with self.conn_lock:
                                    self.conn.sendall((msg_to_send + "\n").encode())
                                for color in buffer_color:
                                    buffer_color[color] = 0
                            except Exception as e:
                                print(f"[CONNECTOR] Failed to send to GUI: {e}")
                                self.conn = None
            except serial.SerialException as e:
                print(f"[CONNECTOR] Serial Error {e}")
                self.running = False
                self.handle_disconnect()
                break
            except Exception as e:
                print(f"[CONNECTOR] Unexpected Error {e}")
                self.running = False
                break
            time.sleep(0.01)


# Example usage:
# conn = Connector()
# conn.send_command("LED ON")
# time.sleep(10)
# conn.stop()
