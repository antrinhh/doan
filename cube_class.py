import os
import math
import numpy as np
import cv2 as cv
import time
from helper_func import extract_red, extract_green, extract_blue, load_calibration
import datetime

cam_matrix, dist_coeffs = load_calibration()

class Cube_2:
    def __init__(self, name, frame, color, boundingbox, contour, save_flag=False, cube_size = 2.5, points_num = 6, epsilon_percentages_arc = 0.08):
        self.name = name
        self.save_flag = save_flag
        self.eps_arc = epsilon_percentages_arc
        self.frame = frame.copy()
        self.color = color
        self.contour = contour
        self.x, self.y, self.w, self.h = cv.boundingRect(self.contour)
        self.ROI = self.frame[self.y - 100:self.y + self.h + 100, self.x - 100:self.x + self.w + 100]
        self.points_num = points_num
        self.cube_size = cube_size
        self.world_points = np.array([[0, 0, 0], [cube_size, 0, 0], [cube_size, 0, -cube_size], 
                        [cube_size, cube_size, -cube_size], [0, cube_size, -cube_size], [0, cube_size, 0],], dtype=float)
        self.surface_points_init()
        self.surface_points_update()
        points = [
            self.top_upper_point,
            self.top_left_point,
            self.bottom_left_point,
            self.bottom_down_point,
            self.bottom_right_point,
            self.top_right_point
        ]

        valid_points = [np.array(pt) for pt in points if pt is not None]
        self.retval, self.rvec, self.tvec = None, None, None
        self.success = False

        self.approx_points = np.array(valid_points, dtype=np.float32)
        for num in [6, 5, 4]:
            try:
                self.retval, self.rvec, self.tvec = cv.solvePnP(self.world_points[:len(self.approx_points)], self.approx_points.astype(np.float32), cam_matrix, dist_coeffs)
                if self.retval is not None:
                    self.distance = np.linalg.norm(self.tvec)
                    text = f"Distance to camera {name, color, num}: {self.distance:.2f} cm"
                    self.success = True
                    break
            except:
                text = f"PnP failed {len(self.approx_points)}"
        print(text)
    
        if self.save_flag:
            self.draw_surface_points()
            print("World points (3D):", self.world_points[:len(self.approx_points)])
            print(f"Approx points (2D): {self.approx_points}")


    def img_process_rgb2canny(self, input_ROI):        
        if self.save_flag:
            cv.imshow("ROI", input_ROI)
            cv.waitKey(0)

        gray = cv.cvtColor(input_ROI, cv.COLOR_RGB2GRAY)
        gray = cv.Canny(gray, 50, 150, apertureSize = 3)    
        if self.save_flag:
            cv.imshow("gray_ROI", gray)
            cv.waitKey(0)
            
        origin_ROI = input_ROI.copy()
        if self.color == 'red':        
            _, color = extract_red(input_ROI)
        if self.color == 'green':        
            _, color = extract_green(input_ROI)
        if self.color == 'blue':        
            _, color = extract_blue(input_ROI)
        if self.save_flag:
            cv.imshow(f"{self.color}", color)
            cv.waitKey(0)
        
        color = cv.GaussianBlur(color, 5)    
        if self.save_flag:
            cv.imshow("medianBlur", color)
            cv.waitKey(0)
        gf_time = time.time()
        color_canny = cv.Canny(color, 50, 150, apertureSize = 3)    
        if self.save_flag:
            cv.imshow("Canny", color)
            cv.waitKey(0)
            
        return color_canny
    
    def approx_6_points(self,):
        img = self.frame.copy()
        contour = self.contour
        eps = self.eps_arc*cv.arcLength(contour, True)
        approx = cv.approxPolyDP(contour, eps, True).reshape(-1, 2)
        if self.save_flag:
            cv.polylines(img, [approx], True, (0, 0, 255), 3)
            cv.imshow('approx_6_point', img)
        return approx
    
    def distance_between_points(self, pt1, pt2):
        pt1 = np.array(pt1)
        pt2 = np.array(pt2)
        return np.linalg.norm(pt1 - pt2)
    
    def surface_points_update(self, ):
        # Example of how to update surface points
        corners = self.approx_6_points()
        data = corners[corners[:, 1].argsort()]
        
        self.top_upper_point = data[0, :]
        if data[1, 0] < data[2, 0]:
            self.top_left_point = data[1, :]
            self.top_right_point = data[2, :]
        else:
            self.top_left_point = data[2, :]
            self.top_right_point = data[1, :]
        
        self.top_down_point = self.top_left_point + self.top_right_point - self.top_upper_point
       

        # Update bottom surface points
        data = corners[corners[:, 1].argsort()]
        self.bottom_down_point = data[-1, :]
        if data[-3, 0] < data[-2, 0]:
            self.bottom_left_point = data[-3, :]
            self.bottom_right_point = data[-2, :]
        else:
            self.bottom_left_point = data[-2, :]
            self.bottom_right_point = data[-3, :]
        


    def surface_points_init(self,):
        self.top_upper_point = None
        self.top_down_point = None
        self.top_left_point = None
        self.top_right_point = None
        
        self.bottom_down_point = None
        self.bottom_left_point = None
        self.bottom_right_point = None
        
    def draw_surface_points(self, save_dir = 'data/output'):
        for i, pt in enumerate(self.approx_points):
            if pt is not None:
                pt_int = tuple(pt.astype(int))
                cv.circle(self.frame, pt_int, 5, (255, 0, 0), -1)  # Draw approx points in red
                cv.putText(self.frame, f"approx_{i}: {pt_int[0], pt_int[1]}", (pt_int[0] + 5, pt_int[1] - 5), cv.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

        if hasattr(self, 'frame') and self.frame is not None:
            os.makedirs(save_dir, exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = os.path.join(save_dir, f"{self.name}_{timestamp}_frame.png")
            cv.imwrite(filename, self.frame)
            print(f"[{self.name}] Frame saved to {filename}")
        return True
    