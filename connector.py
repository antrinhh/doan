import serial
import time
import threading
import serial.tools.list_ports
import re


class Connector:
    def __init__(self, baudrate=9600, timeout=1, listen_flag = 1):
        self.port = self.find_arduino()
        self.baudrate = baudrate
        self.timeout = timeout
        self.arduino = None
        self.running = False  # For thread control
        self.connect_arduino()
        if self.arduino and listen_flag:
            print("Arduino connected")
            self.start_listening()
            

    def connect_arduino(self, retries=5):
        attempts = 0
        while not self.arduino and attempts < retries:
            try:
                self.arduino = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
                time.sleep(2)  
                if self.wait_for_ready():
                    return
                else:
                    self.arduino.close()
                    self.arduino = None
                    return
            except Exception as e:
                print(f"Connection attempt {attempts+1} failed: {e}")
                attempts += 1
                time.sleep(1)
        if not self.arduino:
            print("Failed to connect to Arduino after multiple attempts.")

    def send_cmd(self, cmd):
        if cmd is None:
            print("Cannot send command, no color is detected")
            return
        if self.arduino and self.arduino.is_open:
            command = f"{cmd}\n"
            self.arduino.write(command.encode())
            print(f"Sent: {command.strip()}")
        else:
            print("Arduino not connected")
    
    def send_coords(self, x, y, z):
        if None in [x, y, z]:
            print("Cannot send command. One or more coordinates are None.")
            return
        
        if self.arduino and self.arduino.is_open:
            command = f"{x:.2f},{y:.2f},{z:.2f}\n"  # Command format
            self.arduino.write(command.encode())
            print(f"Sent: {command.strip()}")
        else:
            print("Arduino is not connected")

    def wait_for_ready(self, target_message="Finish setup", timeout=100):
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                if self.arduino and self.arduino.in_waiting > 0:
                    line = self.arduino.readline().decode('utf-8', errors='ignore').strip()
                    print(f"Arduino says: {line}")
                    if target_message in line:
                        print(f"[✓] Message received: {target_message}")
                        return True
            except Exception as e:
                print(f"[wait_for_ready error] {e}")
                return False
        print(f"[!] Timeout waiting for '{target_message}'")
        return False
    
    def start_listening(self):
        self.running = True
        self.listener_thread = threading.Thread(target=self.listen_to_arduino, daemon=True)
        self.listener_thread.start()
        
    def stop(self):
        self.running = False
        if self.arduino and self.arduino.is_open:
            self.arduino.close()
        print("Stopped connection.")

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
        print("Reconnecting to Arduino...")
        self.stop()
        self.port = self.find_arduino()
        self.connect_arduino()
        if self.arduino:
            self.start_listening()
    
    def listen_to_arduino(self):
        while self.running:
            try:
                if self.arduino and self.arduino.in_waiting > 0:
                    line = self.arduino.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        print(f"[←] Arduino says: {line}")
            except serial.SerialException as e:
                print(f"[Serial Error] {e}")
                self.running = False
                self.handle_disconnect()
                break
            except Exception as e:
                print(f"[Unexpected Error] {e}")
                self.running = False
                break
            time.sleep(0.01)


# Example usage:
# conn = Connector()
# conn.send_command("LED ON")
# time.sleep(10)
# conn.stop()
