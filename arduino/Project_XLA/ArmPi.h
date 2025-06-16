#ifndef ARM_PI_H
#define ARM_PI_H
#include <Servo.h>
// #define S1_EN_PIN A1
// Based: 1/8, step/angle = 40 H H L
#define S1_STEP_PIN 2
#define S1_DIR_PIN 5

// #define S2_EN_PIN 6
// Based: 1/16, step/angle = 40 L L H 
#define S2_STEP_PIN 3
#define S2_DIR_PIN 6

// S3 1/8step, ~0.300V, H H L
// Neu theo nhu code goc dieu khien: 1/32 buoc va di qua ti le truyen 2/9 thi dong co phai co step/angle la 80
// #define S3_EN_PIN 9
#define S3_STEP_PIN 4
#define S3_DIR_PIN 7

#define S1_STOP_PIN 9
#define S2_STOP_PIN 10
#define S3_STOP_PIN 11

#define SERVO_PIN 12

#define STEPS_PER_DEGREE_S1 20
#define STEPS_PER_DEGREE_S2 40
#define STEPS_PER_DEGREE_S3 20
#define S1_START -99
#define S2_START 150
#define S3_START 0 // home position is -22 degrees compare to horizontal
#define S4_START -132

#define a4 83.00 //a
#define a3 140.00 //b
#define a2 140.00 //c
#define d1 130.00 //d

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define SERVO_OPEN 80
#define SERVO_CLOSE 0

extern bool s1_stop;
extern float s1_pos;
extern float s1_angle;
extern uint16_t s1_num_steps;
// uint16_t s1_delay_us = 500;

extern bool s2_stop;
extern float s2_pos;
extern float s2_angle;
extern uint16_t s2_num_steps;
// uint16_t s2_delay_us = 1000;

extern bool s3_stop;
extern float s3_pos;
extern float s3_angle;
extern uint16_t s3_num_steps;
extern uint16_t s3_delay_us;

extern float q4;
extern bool color;
extern float x, y, z;
extern bool servo_angle;
extern float pre_alpha;

extern float joint_current[4];
extern float xyz_current[4];
extern float xyz_end_delta[5];
extern float xyz_next[4];
extern char cmd[20];

extern bool debug;
extern bool newData;
extern bool out_of_bound;
extern bool first_move;

void end_to_coords();

void go_home();

void pick_and_drop();

void go_to_pos_end(float x, float y, float z, uint8_t done);

#endif