import serial
import time


class Connector:
    def __init__(self):
        self.arduino = None
        self.ConnectArduino()
        if self.arduino:
            print("Arduino connected")

    def ConnectArduino(self):
        while not self.arduino:
            try:
                self.arduino = serial.Serial("/dev/ttyUSB0", 9600, timeout=1)
                time.sleep(2)
                return self.arduino
            except Exception as e:
                print(f"Error: {e}")

    def SendCommand(self, command):
        command = f"{command}\n"
        self.arduino.write(command.encode())
        print(f"Sent {command.strip()}")
