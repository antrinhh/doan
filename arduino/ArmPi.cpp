#include "ArmPi.h"
#include <Arduino.h>
#include <math.h>

Servo myservo;

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
uint16_t s3_delay_us = 1000;

float q4 = 0;
bool color = false;
float x, y, z;
bool servo_angle = 1;
float pre_alpha = 70;

bool debug = false;
bool newData = false;

float joint_current[4] = {S1_START, S2_START, S3_START, S4_START};
float xyz_current[4] = {121.16, -4.23, 238.92, 0};
float xyz_next[4] = {121.16, -4.23, 238.92, 0};  
float xyz_end_delta[5]; 
char receivedChars[64];             

void updatePosition(float q1, float q2, float q3, float q4) {
  // Input: all are in degree


  joint_current[0] = q1;
  joint_current[1] = q2;
  joint_current[2] = q3;
  joint_current[3] = q4;

  // Convert to radians
  q1 = radians(q1);
  q2 = radians(q2);
  q3 = radians(q3);
  q4 = radians(q4);

  x = a2 * cos(q1) * cos(q2) + a3 * cos(q1) * cos(q2 - q3) + a4 * cos(q1) * cos(q2 - q3 + q4);
  y = a2 * sin(q1) * cos(q2) + a3 * sin(q1) * cos(q2 - q3) + a4 * sin(q1) * cos(q2 - q3 + q4);
  z = d1 + a2 * sin(q2) + a3 * sin(q2 - q3) + a4 * sin(q2 - q3 + q4);
  xyz_current[0] = x;
  xyz_current[1] = y;
  xyz_current[2] = z;
  if(debug){
    Serial.print("x: ");
    Serial.println(x, 2);
    Serial.print("y: ");
    Serial.println(y, 2);
    Serial.print("z: ");
    Serial.println(z, 2);
  }
}

void bool_to_servo(bool a) {
  if (a){
    myservo.write(SERVO_OPEN);
  }
  else myservo.write(SERVO_CLOSE);
}

void end_to_coords() {
  xyz_next[0] = xyz_current[0] + xyz_end_delta[0] * cos(radians(joint_current[0])) + xyz_end_delta[2] * sin(radians(joint_current[0]));
  xyz_next[1] = xyz_current[1] + xyz_end_delta[0] * sin(radians(joint_current[0])) - xyz_end_delta[2] * cos(radians(joint_current[0]));
  xyz_next[2] = xyz_current[2] + xyz_end_delta[1] + 10; 

  
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
    if (s3_stop) digitalWrite(S3_STEP_PIN, LOW);
    delayMicroseconds(s3_delay_us);

    if (s1_stop) digitalWrite(S1_STEP_PIN, LOW);
    if (s2_stop) digitalWrite(S2_STEP_PIN, LOW);
    if (s3_stop) digitalWrite(S3_STEP_PIN, HIGH);
    delayMicroseconds(s3_delay_us);
    if (s3_stop) digitalWrite(S3_STEP_PIN, LOW);
    delayMicroseconds(s3_delay_us);
  }
  myservo.write(SERVO_CLOSE);
  s1_stop = true;
  s2_stop = true; 
  s3_stop = true;
  s1_pos = S1_START; 
  s2_pos = S2_START; 
  s3_pos = S3_START; 
  if(debug){
    Serial.println("Go home: done!");
    Serial.print(", S3 Pos: ");
    Serial.println(s3_pos, 2);
    Serial.print(", S2 Pos: ");
    Serial.println(s2_pos, 2);
    Serial.print(", S1 Pos: ");
    Serial.println(s1_pos, 2);
  }
}

void go_to_pos_end(float x, float y, float z, bool servo_angle) {
  // Tính động học ngược
    float k = pow((sqrt(x * x + y * y) - a4), 2) + pow((z - d1), 2);
    float q2 = degrees(-atan((d1 - z) / (sqrt(x * x + y * y) - a4)) + acos((a2 * a2 + k - a3 * a3) / (2 * a2 * sqrt(k)))); //q2
    float q3 = degrees(abs(acos((-a2 * a2 - a3 * a3 + k) / (2 * a2 * a3)))); //q3
  s1_angle = degrees(atan2(y, x)) - s1_pos;
  s1_pos = degrees(atan2(y, x));
  s2_angle = q2 - s2_pos;
  s2_pos = q2;
  s3_angle = pre_alpha - (180.00 - q3 - abs(s2_angle));
  s3_pos = s3_angle + s3_pos;
  pre_alpha = 180.00 - q3;
  q4 = q3 - q2;

  // if((180.00 - s2_pos) - (s3_pos - 22) <= 40) {
  //   Serial.println("Out of bound");
  //   return;
  // }
  // Positions debug
  if(debug){
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
  }

  // Stepper Dir
  digitalWrite(S1_DIR_PIN, (s1_angle < 0) ? HIGH : LOW); //HIGH == clockwise
  digitalWrite(S2_DIR_PIN, (s2_angle < 0) ? LOW : HIGH);
  digitalWrite(S3_DIR_PIN, (s3_angle < 0) ? LOW : HIGH);

  s1_num_steps = round(abs(s1_angle) * STEPS_PER_DEGREE_S1);
  s2_num_steps = round(abs(s2_angle) * STEPS_PER_DEGREE_S2);
  s3_num_steps = round(abs(s3_angle) * STEPS_PER_DEGREE_S3);

  long max_steps = max(s2_num_steps, s3_num_steps);
  long s2_counter = 0;
  long s3_counter = 0;

  while (s1_num_steps || s2_num_steps || s3_num_steps) {
    if (s1_num_steps) digitalWrite(S1_STEP_PIN, HIGH);
    if (s2_num_steps) digitalWrite(S2_STEP_PIN, HIGH);
    if (s3_num_steps) digitalWrite(S3_STEP_PIN, HIGH);
    delayMicroseconds(s3_delay_us);
    if (s3_num_steps) digitalWrite(S3_STEP_PIN, LOW);
    delayMicroseconds(s3_delay_us);
    if (s3_num_steps) s3_num_steps--;

    if (s1_num_steps) digitalWrite(S1_STEP_PIN, LOW);
    if (s2_num_steps) digitalWrite(S2_STEP_PIN, LOW);
    if (s3_num_steps) digitalWrite(S3_STEP_PIN, HIGH);
    delayMicroseconds(s3_delay_us);
    if (s3_num_steps) digitalWrite(S3_STEP_PIN, LOW);
    delayMicroseconds(s3_delay_us);

    if (s1_num_steps) s1_num_steps--;
    if (s2_num_steps) s2_num_steps--;
    if (s3_num_steps) s3_num_steps--;
  }

  if(debug){
    Serial.println("done!");
    Serial.println("X: " + String(x, 2) + ", Y: " + String(y, 2) + ", Z: " + String(z, 2));
  }
  // Control servo
  bool_to_servo(servo_angle);

  // update array
  updatePosition(s1_pos, s2_pos, q3, q4);
}

void pick_and_drop() {

  end_to_coords();

  Serial.println("X: " + String(xyz_next[0], 2) + ", Y: " + String(xyz_next[1], 2) + ", Z: " + String(xyz_next[2], 2));
  go_to_pos_end(xyz_next[0], xyz_next[1], xyz_next[2], 1);
  Serial.println("s1_angle: " + String(s1_angle, 4));
  Serial.println("s2_angle: " + String(s2_angle, 4));
  Serial.println("s3_angle: " + String(s3_angle, 4));

  // Serial.println("X: " + String(x, 2) + ", Y: " + String(y, 2) + ", Z: " + String(z, 2));
  // go_to_pos(x, y, z, 95);
  // Serial.println("s1_angle: " + String(s1_angle, 4));
  // Serial.println("s2_angle: " + String(s2_angle, 4));
  // Serial.println("s3_angle: " + String(s3_angle, 4));

  delay(1000);
  myservo.write(SERVO_CLOSE);
  // Serial.println("X: " + String(x, 2) + ", Y: " + String(y, 2) + ", Z: " + String(0, 2));
  // go_to_pos(x, y, 0, SERVO_CLOSE);
  // Serial.println("s1_angle: " + String(s1_angle, 4));
  // Serial.println("s2_angle: " + String(s2_angle, 4));
  // Serial.println("s3_angle: " + String(s3_angle, 4));

  if (color) {
    Serial.println("X: 0, Y: 60, Z: 50");
    go_to_pos_end(0, 60, 50, 1);
    Serial.println("s1_angle: " + String(s1_angle, 4));
    Serial.println("s2_angle: " + String(s2_angle, 4));
    Serial.println("s3_angle: " + String(s3_angle, 4));
  } else {
    Serial.println("X: 0, Y: 60, Z: 50");
    go_to_pos_end(0, 60, 50, 1);
    Serial.println("s1_angle: " + String(s1_angle, 4));
    Serial.println("s2_angle: " + String(s2_angle, 4));
    Serial.println("s3_angle: " + String(s3_angle, 4));
  }
  Serial.println("Done!");
} 

void recvWithEndMarker() {
  static byte ndx = 0;
  char endMarker = '\n';
  char rc;

  while (Serial.available() > 0 && !newData) {
    rc = Serial.read();
    if (rc == endMarker) {
      receivedChars[ndx] = '\0';  // terminate the string
      ndx = 0;
      newData = true;             // signal that data is ready
    } else {
      if (ndx < sizeof(receivedChars) - 1) {
        receivedChars[ndx++] = rc;
      }
    }
  }
}

void parseData() {
  char * strtokIndx; 

  strtokIndx = strtok(receivedChars, ",");
  xyz_end_delta[0] = atof(strtokIndx);

  strtokIndx = strtok(NULL, ",");
  xyz_end_delta[1] = atof(strtokIndx);

  strtokIndx = strtok(NULL, ",");
  xyz_end_delta[2] = atof(strtokIndx);

  strtokIndx = strtok(NULL, ",");
  xyz_end_delta[3] = atoi(strtokIndx);

  strtokIndx = strtok(NULL, ",");
  xyz_end_delta[4] = atoi(strtokIndx);

  Serial.print("X: "); Serial.println(xyz_end_delta[0]);
  Serial.print("Y: "); Serial.println(xyz_end_delta[1]);
  Serial.print("Z: "); Serial.println(xyz_end_delta[2]);
  Serial.print("Move: "); Serial.println(xyz_end_delta[3]);
  Serial.print("Open: "); Serial.println(xyz_end_delta[4]);
}