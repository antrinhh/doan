import numpy as np
import math
import time

d1 = 130
a2 = 140
a3 = 140
a4 = 75

x = 150
y = 0
z = 40
start = time.time()
q1 = math.atan2(y, x)
r = math.sqrt(x**2+y**2)-a4
D = (r**2+(z-d1)**2 - a2**2-a3**2)/(2*a2*a3)
q3 = math.atan2(math.sqrt(1-D**2), D)

alpha = math.atan2(a3*math.sin(q3)/r, (a2+a3*math.cos(q3))/r)
beta = math.atan2(z-d1, r)
q2 = alpha+beta
q4 = q3 - q2
stop = time.time()
# print(stop - start)
print(math.degrees(q1))
print(math.degrees(q2))
print(math.degrees(q3))
print(math.degrees(q4))
if 180.00 - math.degrees(q3) <= 13 or math.degrees(q2) < 0:
    print("Failed")
# q4 = 2*math.pi - q4

x_test = a3*math.cos(q1)*math.cos(q2-q3) + a2*math.cos(q1) * \
    math.cos(q2) + a4*math.cos(q1)*math.cos(q2-q3+q4)
y_test = a3*math.sin(q1)*math.cos(q2-q3) + a2*math.sin(q1) * \
    math.cos(q2) + a4*math.sin(q1)*math.cos(q2-q3+q4)
z_test = d1+a2*math.sin(q2)+a3*math.sin(q2-q3)+a4*math.sin(q2-q3+q4)
print(x_test)
print(y_test)
print(z_test)
