#include "ArmPi.h"
#include <Arduino.h>
#include <math.h>

bool s1_stop = true;
float s1_pos = S1_START;
float s1_angle = 0;
uint16_t s1_num_steps = 0;
// uint16_t s1_delay_us = 500;

bool s2_stop = true;
float s2_pos = S2_START;
float s2_angle = 0;
uint16_t s2_num_steps = 0;
// uint16_t s2_delay_us = 1000;

bool s3_stop = true;
float s3_pos = S3_START;
float s3_angle = 0;
uint16_t s3_num_steps = 0;
uint16_t s3_delay_us = 1200;

float q4 = 0;
bool color = false;
float x, y, z;
float pre_alpha = 62;

bool debug = true;
bool newData = false;
bool out_of_bound = false;
bool first_move = true;

float joint_current[4] = {S1_START, S2_START, S3_START, S4_START};
float xyz_current[4] = {121.16, -4.23, 238.92, 0};
float xyz_next[4] = {121.16, -4.23, 238.92, 0};  
char cmd[20];             

void end_to_coords() {
  xyz_next[0] = xyz_current[0] + xyz_end_delta[0] * cos(radians(joint_current[0])) + xyz_end_delta[2] * sin(radians(joint_current[0])) - 10;
  xyz_next[1] = (xyz_current[1] + xyz_end_delta[0] * sin(radians(joint_current[0])) - xyz_end_delta[2] * cos(radians(joint_current[0])));
  xyz_next[2] = xyz_current[2] + xyz_end_delta[1] - 20; 
}

void go_home() {
  // digitalWrite(S1_EN_PIN, LOW);
  // digitalWrite(S2_EN_PIN, LOW);
  // digitalWrite(S3_EN_PIN, LOW);
  digitalWrite(S1_DIR_PIN, HIGH);
  digitalWrite(S2_DIR_PIN, HIGH);
  digitalWrite(S3_DIR_PIN, LOW);
  while (s1_stop || s2_stop || s3_stop) {
    s1_stop = digitalRead(S1_STOP_PIN);
    s2_stop = digitalRead(S2_STOP_PIN);
    s3_stop = digitalRead(S3_STOP_PIN);

    if (s1_stop) digitalWrite(S1_STEP_PIN, HIGH);
    if (s2_stop) digitalWrite(S2_STEP_PIN, HIGH);
    if (s3_stop) digitalWrite(S3_STEP_PIN, HIGH);
    delayMicroseconds(s3_delay_us);
    if (s2_stop) digitalWrite(S2_STEP_PIN, LOW);
    delayMicroseconds(s3_delay_us);
    if (s2_stop) digitalWrite(S2_STEP_PIN, HIGH);
    delayMicroseconds(s3_delay_us);

    if (s1_stop) digitalWrite(S1_STEP_PIN, LOW);
    if (s2_stop) digitalWrite(S2_STEP_PIN, LOW);
    if (s3_stop) digitalWrite(S3_STEP_PIN, LOW);
    delayMicroseconds(s3_delay_us);
  }
  s1_stop = true;
  s2_stop = true; 
  s3_stop = true;
  s1_pos = S1_START; 
  s2_pos = S2_START; 
  s3_pos = S3_START; 
  if(debug){
    Serial.println("Go home: done!");
    Serial.print("S3 Pos: ");
    Serial.println(s3_pos, 2);
    Serial.print("S2 Pos: ");
    Serial.println(s2_pos, 2);
    Serial.print("S1 Pos: ");
    Serial.println(s1_pos, 2);
  }
}

void go_to_pos_end(float x, float y, float z, uint8_t done) {
  // Tính động học ngược
  float k = pow((sqrt(x * x + y * y) - a4), 2) + pow((z - d1), 2);
  float q2 = degrees(-atan((d1 - z) / (sqrt(x * x + y * y) - a4)) + acos((a2 * a2 + k - a3 * a3) / (2 * a2 * sqrt(k)))); //q2
  float q3 = degrees(abs(acos((-a2 * a2 - a3 * a3 + k) / (2 * a2 * a3)))); //q3
  float temp = acos((-a2 * a2 - a3 * a3 + k) / (2 * a2 * a3));
  s1_angle = degrees(atan2(y, x)) - s1_pos;
  s1_pos = degrees(atan2(y, x));
  s2_angle = q2 - s2_pos;
  s2_pos = q2;
  if(s2_angle <= 0){
    s3_angle = pre_alpha - (180.00 - q3 - abs(s2_angle));
    s3_pos = s3_angle + s3_pos;
    pre_alpha = 180.00 - q3;
  }
  else{
    s3_angle = pre_alpha - (180.00 - q3 + abs(s2_angle));
    s3_pos = s3_angle + s3_pos;
    pre_alpha = 180.00 - q3;
  }
  q4 = q3 - q2;
  first_move = false;

  if((180.00 - q3) <= 2.00 || (180.00 - q3) >= 148.0 || isnan(q2) || q2 < 5.00) {
    Serial.println("Out of bound");
    Serial.println(180.00-q3);
    Serial.print("S3 Angle: ");
    Serial.print(s3_angle, 2);
    Serial.print(", S3 Pos: ");
    Serial.println(s3_pos, 2);

    Serial.print("S2 Angle: ");
    Serial.print(s2_angle, 2);
    Serial.print(", S2 Pos: ");
    Serial.println(s2_pos, 2);

    Serial.print("S1 Angle: ");
    Serial.print(s1_angle, 2);
    Serial.print(", S1 Pos: ");
    Serial.println(s1_pos, 2);
    out_of_bound = true;
    return;
  }

  // Stepper Dir
  digitalWrite(S1_DIR_PIN, (s1_angle < 0) ? HIGH : LOW); //HIGH == clockwise
  digitalWrite(S2_DIR_PIN, (s2_angle < 0) ? LOW : HIGH);
  digitalWrite(S3_DIR_PIN, (s3_angle < 0) ? LOW : HIGH);

  s1_num_steps = round(abs(s1_angle) * STEPS_PER_DEGREE_S1);
  s2_num_steps = round(abs(s2_angle) * STEPS_PER_DEGREE_S2);
  s3_num_steps = round(abs(s3_angle) * STEPS_PER_DEGREE_S3);

  if(debug){
    Serial.print("S3 Angle: ");
    Serial.print(s3_angle, 2);
    Serial.print(", Steps: ");
    Serial.print(s3_num_steps);
    Serial.print(", S3 Pos: ");
    Serial.println(s3_pos, 2);

    Serial.print("S2 Angle: ");
    Serial.print(s2_angle, 2);
    Serial.print(", Steps: ");
    Serial.print(s2_num_steps);
    Serial.print(", S2 Pos: ");
    Serial.println(s2_pos, 2);

    Serial.print("S1 Angle: ");
    Serial.print(s1_angle, 2);
    Serial.print(", Steps: ");
    Serial.print(s1_num_steps);
    Serial.print(", S1 Pos: ");
    Serial.println(s1_pos, 2);
  }

  while (s1_num_steps || s2_num_steps || s3_num_steps) {
    if (s1_num_steps) digitalWrite(S1_STEP_PIN, HIGH);
    if (s2_num_steps) digitalWrite(S2_STEP_PIN, HIGH);
    if (s3_num_steps) digitalWrite(S3_STEP_PIN, HIGH);
    delayMicroseconds(s3_delay_us);
    if (s2_num_steps) digitalWrite(S2_STEP_PIN, LOW);
    delayMicroseconds(s3_delay_us);
    if (s2_num_steps) s2_num_steps--;

    if (s2_num_steps) digitalWrite(S2_STEP_PIN, HIGH);
    delayMicroseconds(s3_delay_us);

    if (s1_num_steps) digitalWrite(S1_STEP_PIN, LOW);
    if (s2_num_steps) digitalWrite(S2_STEP_PIN, LOW);
    if (s3_num_steps) digitalWrite(S3_STEP_PIN, LOW);
    delayMicroseconds(s3_delay_us);

    if (s1_num_steps) s1_num_steps--;
    if (s2_num_steps) s2_num_steps--;
    if (s3_num_steps) s3_num_steps--;
  }

  if(debug){
    Serial.println("X: " + String(x, 2) + ", Y: " + String(y, 2) + ", Z: " + String(z, 2));
  }
  
  if(done){
    Serial.println("Done!");
  }

}

void pick_and_drop() {

  go_to_pos_end(260, 0, 78, 1);
  delay(1000);
  delay(2000);

  if (xyz_end_delta[4] == 1) {
    Serial.println("X: 200, Y: 200, Z: 50");
    go_to_pos_end(100, -200, 50, 1);
    Serial.println("s1_angle: " + String(s1_angle, 4));
    Serial.println("s2_angle: " + String(s2_angle, 4));
    Serial.println("s3_angle: " + String(s3_angle, 4));
  }
  else if (xyz_end_delta[4] == 2) {
    Serial.println("X: 0, Y: 200, Z: 50");
    go_to_pos_end(0, -200, 50, 1);
    Serial.println("s1_angle: " + String(s1_angle, 4));
    Serial.println("s2_angle: " + String(s2_angle, 4));
    Serial.println("s3_angle: " + String(s3_angle, 4));
  }
  else if (xyz_end_delta[4] == 3) {
    Serial.println("X: -200, Y: 200, Z: 50");
    go_to_pos_end(-100, -200, 50, 1);
    Serial.println("s1_angle: " + String(s1_angle, 4));
    Serial.println("s2_angle: " + String(s2_angle, 4));
    Serial.println("s3_angle: " + String(s3_angle, 4));
  }
  Serial.println("Done pickup!");
} 
