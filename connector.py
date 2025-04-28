import serial
import time
import threading


class Connector:
    def __init__(self, port="/dev/ttyUSB0", baudrate=9600, timeout=1):
        self.port = port
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

    def send_command(self, command):
        if self.arduino and self.arduino.is_open:
            command = f"{command}\n"
            self.arduino.write(command.encode())
            print(f"Sent: {command.strip()}")
        else:
            print("Cannot send command. Arduino is not connected.")

    def listen_to_arduino(self):
        while self.running:
            if self.arduino and self.arduino.in_waiting > 0:
                try:
                    message = self.arduino.readline().decode('utf-8').strip()
                    if message:
                        print(f"Arduino says: {message}")
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


# Example usage:
# conn = Connector()
# conn.send_command("LED ON")
# time.sleep(10)
# conn.stop()
