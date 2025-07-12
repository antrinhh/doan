import cv2 as cv
import numpy as np
import os
from gpiozero import Servo
from time import sleep
from gpiozero.pins.pigpio import PiGPIOFactory


def load_calibration():
    param_path = os.path.join(os.getcwd(), 'calibration.npz')
    param_data = np.load(param_path)
    return param_data['camMatrix'], param_data['distCoeff']

# Power law transfrom - Gamma Correction: a technique to adjust the brightness and the contrast of the image
# O = I^(1/G)
def adjust_gamma(img, gamma = 1.0): 
    invGamma = 1/gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
		for i in np.arange(0, 256)]).astype("uint8")
    return cv.LUT(img, table)

def extract_red(img):
    hsv_img = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    
    # Red at 0 degree
    lower_red = np.array([0, 43, 46]) #lower_red = np.array([0, 161, 79])
    upper_red = np.array([6, 255, 255])
    mask_1 = cv.inRange(hsv_img, lower_red, upper_red)

    # Red at 360 degree
    lower_red = np.array([156, 43, 46]) #lower_red = np.array([173, 200, 84])
    upper_red = np.array([179, 255, 255])
    mask_2 = cv.inRange(hsv_img, lower_red, upper_red)

    mask = cv.bitwise_or(mask_1, mask_2)

    img = cv.bitwise_and(img, img, mask=mask)

    combined_masks = cv.hconcat([mask_1, mask_2])
    #cv.imshow("Mask 1 (Low Red) | Mask 2 (High Red)", combined_masks)
    # cv.destroyAllWindows()
    return mask

def extract_blue(img):
    hsv_img = cv.cvtColor(img, cv.COLOR_BGR2HSV)

    lower_blue = np.array([90, 43, 46])
    upper_blue = np.array([110, 255, 255])

    mask = cv.inRange(hsv_img, lower_blue, upper_blue)
    img = cv.bitwise_and(img, img, mask=mask)

    return mask

def extract_green(img):
    img_hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

    lower_green=np.array([35,43,46])
    upper_green=np.array([77,255,255])

    mask = cv.inRange(img_hsv, lower_green, upper_green)
    img = cv.bitwise_and(img, img, mask=mask)

    return mask

def mask_3_colors(img):
    mask_red, _ = extract_red(img)
    mask_blue, _ = extract_blue(img)
    mask_green, _ = extract_green(img)

    mask = cv.bitwise_or(mask_green, mask_blue)
    mask = cv.bitwise_or(mask, mask_red)

    mask = morp_noise(mask)
    green = morp_noise(mask_green)
    blue = morp_noise(mask_blue)
    red = morp_noise(mask_red)

    return mask, green, blue, red

def morp_noise(binary_img, kernel_size = (3, 3)):
    kernel = np.ones((kernel_size))
    open = cv.morphologyEx(binary_img, cv.MORPH_OPEN, kernel)
    close = cv.morphologyEx(open, cv.MORPH_CLOSE, kernel)

    kernel = np.ones((5, 5))
    erode = cv.morphologyEx(close, cv.MORPH_ERODE, kernel)

    erode = cv.morphologyEx(erode, cv.MORPH_CLOSE, (9, 9))
    return erode

def gray_3_colors(frame):
    mask, mask_green, mask_blue, mask_red = mask_3_colors(frame)

    frame_red = cv.bitwise_and(frame, frame, mask=mask_red)
    frame_blue = cv.bitwise_and(frame, frame, mask=mask_blue)
    frame_green = cv.bitwise_and(frame, frame, mask=mask_green)
    # frame = cv.bitwise_and(frame, frame, mask=mask)

    gray_red = cv.cvtColor(frame_red, cv.COLOR_BGR2GRAY)
    gray_blue = cv.cvtColor(frame_blue, cv.COLOR_BGR2GRAY)
    gray_green = cv.cvtColor(frame_green, cv.COLOR_BGR2GRAY)

    return gray_red, gray_blue, gray_green

def is_closed_contour(contour, tolerance=10):
    if len(contour) >= 3:
        start = contour[0][0]
        end = contour[-1][0]
        dist = np.linalg.norm(start - end)
        return dist < tolerance
    return False

def angle_to_value(angle):
    """Converts an angle (0 to 180) to servo.value (-1 to 1)."""
    return (angle - 90) / 90

import cv2 as cv
import numpy as np
from math import sin, cos, atan2, sqrt, degrees, radians, pi

###################################
#   Khau   ##   qi  ##  di  ##  ai  ##  alpha
#   1      ##   q1  ##  d1  ##  0   ##  pi/2
#   2      ##   q2  ##  0   ##  a2  ##  pi
#   3      ##   q3  ##  0   ##  a3  ##  pi
#   4      ##   q4  ##  0   ##  a4  ##  0
#  camera  ##


d1 = 130
a2 = 140
a3 = 140
a4 = 84

x_end_cam = 5
y_end_cam = 34
z_end_cam = 0


def get_homogeous_matrix(rvec, tvec):
    R, _ = cv.Rodrigues(rvec)  # Convert to 3x3 rotation matrix
    H = np.eye(4)
    H[:3, :3] = R
    H[:3, 3] = tvec.flatten()
    return H


def Homogeous_end_to_cam(): # Rotate Ry(90) x Rotate Rz(180) x Rx(-32)
    H = np.array([[0,       0.5299,      0.848,      -x_end_cam],
                  [0,       -0.848,     0.5299,      y_end_cam],
                  [1,       0,      0,      z_end_cam],
                  [0,       0,      0,      1]], dtype=np.float32)
    return H

def z_180():
    H = np.array([[-1,       0,      0],
                  [0,       -1,     0],
                  [0,       0,      1],], dtype=np.float32)
    return H

def ForwardKinematics(q1, q2, q3, q4):
    H = np.array([[cos(q1) * cos(q2 - q3 + q4),     -cos(q1) * sin(q2 - q3 + q4),        sin(q1),       a2 * cos(q1) * cos(q2) + a3 * cos(q1) * cos(q2 - q3) + a4 * cos(q1) * cos(q2 - q3 + q4)],
                  [sin(q1) * cos(q2 - q3 + q4),     -sin(q1) * sin(q2 - q3 + q4),       -cos(q1),
                   a2 * sin(q1) * cos(q2) + a3 * sin(q1) * cos(q2 - q3) + a4 * sin(q1) * cos(q2 - q3 + q4)],
                  [sin(q2 - q3 + q4),               cos(q2 - q3 + q4),                  0,
                   d1 + a2 * sin(q2) + a3 * sin(q2 - q3) + a4 * sin(q2 - q3 + q4)],
                  [0,                               0,                                  0,              1]], dtype=np.float32)
    return H


def InverseKinematics(x, y, z):
    q1 = atan2(y, x)
    r = sqrt(x**2 + y**2) - a4
    D = (r**2 + (z - d1)**2 - a2**2 - a3**2)/(2 * a2 * a3)
    q3 = atan2(sqrt(1 - D**2), D)

    alpha = atan2(a3 * sin(q3)/r, (a2 + a3 * cos(q3))/r)
    beta = atan2(z - d1, r)
    q2 = alpha + beta
    q4 = q3 - alpha - beta
    return q1, q2, q3, q4


def main():
    q1_test, q2_test, q3_test, q4_test = InverseKinematics(300, 0, 250)
    x_test, y_test, z_test = ForwardKinematics(
        q1_test, q2_test, q3_test, q4_test)
    print(f"q1 = {degrees(q1_test)}\nq2 = {degrees(q2_test)}\nq3 = {degrees(q3_test)}\nq4 = {degrees(q4_test)}")
    print(f"x = {x_test}\ny = {y_test}\nz = {z_test}")


if __name__ == "__main__":
    factory = PiGPIOFactory()
    servo = Servo(18, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=factory)
    servo.value = angle_to_value(70)

