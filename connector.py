import serial
import time
import threading
import serial.tools.list_ports
import re


class Connector:
    def __init__(self, baudrate=9600, timeout=1):
        self.port = self.find_arduino()
        self.baudrate = baudrate
        self.timeout = timeout
        self.arduino = None
        self.running = False  # For thread control
        self.connect_arduino()
        if self.arduino:
            print("Arduino connected")
            self.start_listening()

    def connect_arduino(self, retries=5):
        attempts = 0
        while not self.arduino and attempts < retries:
            try:
                self.arduino = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
                time.sleep(2)  # Give Arduino time to reset
                return
            except Exception as e:
                print(f"Connection attempt {attempts+1} failed: {e}")
                attempts += 1
                time.sleep(1)
        if not self.arduino:
            print("Failed to connect to Arduino after multiple attempts.")

    def send_command(self, x, y, z):
        if None in [x, y, z]:
            print("Cannot send command. One or more coordinates are None.")
            return
        
        if self.arduino and self.arduino.is_open:
            command = f"{x} {y} {z}\n"  # Construct the command string with coordinates
            self.arduino.write(command.encode())
            print(f"Sent: {command.strip()}")
        else:
            print("Cannot send command. Arduino is not connected.")

    def listen_to_arduino(self):
        # Initialize the position values
        self.x_pos = 0.0
        self.y_pos = 0.0
        self.z_pos = 0.0

        while self.running:
            if self.arduino and self.arduino.in_waiting > 0:
                try:
                    message = self.arduino.readline().decode('utf-8').strip()
                    if message:
                        print(f"Arduino says: {message}")
                        
                        # Use regular expression to capture x, y, z values
                        x_match = re.search(r"x:\s*(-?\d+\.?\d*)", message)
                        y_match = re.search(r"y:\s*(-?\d+\.?\d*)", message)
                        z_match = re.search(r"z:\s*(-?\d+\.?\d*)", message)

                        # Parse and update positions if they are found
                        if x_match:
                            try:
                                self.x_pos = float(x_match.group(1))
                                print(f"Updated x: {self.x_pos}")
                            except Exception as e:
                                print(f"Failed to parse x: {e}")

                        if y_match:
                            try:
                                self.y_pos = float(y_match.group(1))
                                print(f"Updated y: {self.y_pos}")
                            except Exception as e:
                                print(f"Failed to parse y: {e}")

                        if z_match:
                            try:
                                self.z_pos = float(z_match.group(1))
                                print(f"Updated z: {self.z_pos}")
                            except Exception as e:
                                print(f"Failed to parse z: {e}")
                except Exception as e:
                    print(f"Error reading from Arduino: {e}")



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
        return None


    


# Example usage:
# conn = Connector()
# conn.send_command("LED ON")
# time.sleep(10)
# conn.stop()
