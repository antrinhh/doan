import cv2 as cv
import os
import numpy as np

# Define world's variables
cube_size = 2.5
cube_points = np.array([
    [0, 0, 0], [cube_size, 0, 0], [cube_size, cube_size, 0], [0, cube_size, 0],  # Base
    [0, 0, cube_size], [cube_size, 0, cube_size], [cube_size, cube_size, cube_size], [0, cube_size, cube_size]  # Top
], dtype=np.float32)

axis = np.float32([
    [6, 0, 0], [0, 6, 0], [0, 0, 6]  # Extended axes for visibility
])

def load_calibration():
    param_path = os.path.join(os.getcwd(), 'calibration.npz')
    param_data = np.load(param_path)
    return param_data['camMatrix'], param_data['distCoeff']

def draw_axes(frame, cam_matrix, dist_coeffs, rvecs, tvecs, cube_corners):
    imgpts, _ = cv.projectPoints(axis, rvecs, tvecs, cam_matrix, dist_coeffs)
    origin = tuple(cube_corners[0].ravel().astype(int))
    frame = cv.line(frame, origin, tuple(imgpts[0].ravel().astype(int)), (0, 0, 255), 3)  # X (Red)
    frame = cv.line(frame, origin, tuple(imgpts[1].ravel().astype(int)), (0, 255, 0), 3)  # Y (Green)
    frame = cv.line(frame, origin, tuple(imgpts[2].ravel().astype(int)), (255, 0, 0), 3)  # Z (Blue)
    return frame

# Preprocessing to enhance edge detection
def preprocess_frame(frame):
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    blurred = cv.GaussianBlur(gray, (5, 5), 0)  # Reduce noise
    edges = cv.Canny(blurred, 50, 150)  # Apply Canny Edge Detection

    # Morphological operations to enhance edges
    kernel = np.ones((3, 3), np.uint8)
    edges = cv.dilate(edges, kernel, iterations=1)
    edges = cv.erode(edges, kernel, iterations=1)

    return edges

# HSV Thresholding for Blue Cube
def threshold_cube(frame):
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    lower_blue = np.array([90, 50, 50])
    upper_blue = np.array([130, 255, 255])
    mask = cv.inRange(hsv, lower_blue, upper_blue)
    
    # Apply morphology to clean up noise
    kernel = np.ones((5, 5), np.uint8)
    mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, kernel)
    return mask

# Find Cube Contours
def get_cube_contours(mask):
    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    
    contour_frame = np.zeros(mask.shape, dtype=np.uint8)  # Blank image for contours visualization
    cv.drawContours(contour_frame, contours, -1, 255, 1)  # Draw all contours in white

    for cnt in contours:
        if cv.contourArea(cnt) > 500:
            approx = cv.approxPolyDP(cnt, 0.02 * cv.arcLength(cnt, True), True)
            if len(approx) == 4:  # Detecting a quadrilateral (potential cube face)
                return approx.reshape(-1, 2), contours, contour_frame  # Return cube corners, all contours, and contour image

    return None, contours, contour_frame

def position_estimation(frame, cube_corners, cam_matrix, dist_coeffs):
    if cube_corners is None or cube_corners.shape != (4, 2):
        return None, None  # No object detected

    retval, rvec, tvec, _ = cv.solvePnPRansac(cube_points[:4], cube_corners.astype(np.float32), cam_matrix, dist_coeffs)

    if retval:
        frame = draw_axes(frame, cam_matrix, dist_coeffs, rvec, tvec, cube_corners)
    return rvec, tvec

def main():
    cam_matrix, dist_coeffs = load_calibration()
    cap = cv.VideoCapture(1)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        original_frame = frame.copy()  # Copy for original view

        # Preprocess frame for edge detection
        edges = preprocess_frame(frame)

        # Detect cube using HSV thresholding
        mask = threshold_cube(frame)

        # Get cube contours
        cube_corners, contours, contour_frame = get_cube_contours(mask)

        if cube_corners is not None:
            cv.drawContours(frame, [cube_corners], -1, (255, 0, 0), 2)
            position_estimation(frame, cube_corners, cam_matrix, dist_coeffs)

        # Display all process steps
        # cv.imshow('Original Frame', original_frame)
        cv.imshow('HSV Mask (Color Detection)', mask)
        cv.imshow('Edge Detection (Canny)', edges)
        # cv.imshow('Contours Detection', contour_frame)
        cv.imshow('Final Output (Pose Estimation)', frame)

        if cv.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv.destroyAllWindows()

if __name__ == '__main__':
    main()
