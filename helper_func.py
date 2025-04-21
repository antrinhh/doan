import cv2 as cv
import numpy as np
import os


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
    return mask, img

def extract_blue(img):
    hsv_img = cv.cvtColor(img, cv.COLOR_BGR2HSV)

    lower_blue = np.array([90, 43, 46])
    upper_blue = np.array([110, 255, 255])

    mask = cv.inRange(hsv_img, lower_blue, upper_blue)
    img = cv.bitwise_and(img, img, mask=mask)

    return mask, img

def extract_green(img):
    img_hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

    lower_green=np.array([35,43,46])
    upper_green=np.array([77,255,255])

    mask = cv.inRange(img_hsv, lower_green, upper_green)
    img = cv.bitwise_and(img, img, mask=mask)

    return mask, img

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
