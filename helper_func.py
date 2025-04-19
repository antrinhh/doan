import cv2 as cv
import numpy as np


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
    cv.imshow("Mask 1 (Low Red) | Mask 2 (High Red)", combined_masks)
    cv.destroyAllWindows()
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
