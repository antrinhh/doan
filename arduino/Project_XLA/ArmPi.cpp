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
float pre_alpha = 59;

bool debug = false;
bool newData = false;
bool out_of_bound = false;
bool first_move = true;
bool isFullCommand = false;
char charCommand = '\0';

float joint_current[4] = {S1_START, S2_START, S3_START, S4_START};
float xyz_current[3] = {121.16, -4.23, 238.92};
float xyz_next[3] = {121.16, -4.23, 238.92}; 
float xyz[3] = {0, 0, 0}; 
char cmd[20];
char receivedChars[48];              

int b_nums;
int g_nums;
int r_nums;

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
  b_nums = 0;
  g_nums = 0;
  r_nums = 0;
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
    Serial.println("X: " + String(x, 2) + ", Y: " + String(y, 2) + ", Z: " + String(z - 30, 2));
  }

  if(!debug){
    Serial.println("Coordinates: " + String(x, 2) + "," + String(y, 2) + "," + String(z - 30, 2));
    Serial.println("Positions: " + String(s1_pos, 2) + "," + String(s2_pos, 2) + "," + String(s3_pos, 2));
    Serial.println("Variables: " + String(s1_pos, 2) + "," + String(s2_pos, 2) + "," + String(q3, 2) + "," + String(q4, 2));
  }

  updatePosition(s1_pos, s2_pos, q3, q4, x, y, z);
  if(done){
    Serial.println("Done!");
  }

}

void recvWithEndMarker() {
  static byte ndx = 0;
  char endMarker = '\n';
  char rc;

  while (Serial.available() > 0 && ndx < sizeof(cmd) - 1) {
    rc = Serial.read();
    if (rc == endMarker) {
      cmd[ndx] = '\0';  // Null-terminate the string
      ndx = 0;

      // Debug print to see what was received
      Serial.print("Received cmd: ");
      Serial.println(cmd);

      // Determine whether it's a full command or a char command
      if (strchr(cmd, ',') != NULL) {
        isFullCommand = true;
        Serial.println("Detected full command.");
      } else if (strlen(cmd) == 1) {
        charCommand = cmd[0];
        isFullCommand = false;
        Serial.println("Detected char command.");
      } else {
        isFullCommand = false; // Fallback case
        Serial.println("Unknown command format.");
      }

      newData = true;
      break;
    } else {
      cmd[ndx++] = rc;
    }
  }
}

void parseData() {
  char * strtokIndx; 

  strtokIndx = strtok(cmd, ",");
  xyz[0] = atof(strtokIndx);

  strtokIndx = strtok(NULL, ",");
  xyz[1] = atof(strtokIndx);

  strtokIndx = strtok(NULL, ",");
  xyz[2] = atof(strtokIndx);

  Serial.print("X: "); Serial.println(xyz[0]);
  Serial.print("Y: "); Serial.println(xyz[1]);
  Serial.print("Z: "); Serial.println(xyz[2]);

  end_to_coords();
  
  Serial.print("X_next: "); Serial.println(xyz_next[0]);
  Serial.print("Y_next: "); Serial.println(xyz_next[1]);
  Serial.print("Z_next: "); Serial.println(xyz_next[2]);
}

void end_to_coords() {
  Serial.println(xyz_current[2]);
  xyz_next[0] = xyz_current[0] + xyz[0] * cos(radians(joint_current[0])) + xyz[2] * sin(radians(joint_current[0]));
  xyz_next[1] = (xyz_current[1] + xyz[0] * sin(radians(joint_current[0])) - xyz[2] * cos(radians(joint_current[0])));
  // xyz_next[2] = xyz_current[2] + xyz[1] - 80;
  xyz_next[2] = 60; 
}

void updatePosition(float q1, float q2, float q3, float q4, float x, float y, float z) {
  // Input: all are in degree
  joint_current[0] = q1;
  joint_current[1] = q2;
  joint_current[2] = q3;
  joint_current[3] = q4;

  xyz_current[0] = x;
  xyz_current[1] = y;
  xyz_current[2] = z;
}



void handleCharCommand(char inputvalue){
  if(inputvalue == '\n' || inputvalue == '\r') return;

    if(inputvalue == 'y'){
      debug = !debug;
    }

    if(inputvalue == 'i'){
      go_home();  
      go_to_pos_end(180, 0, 60, 1);
      delay(2000);
      Serial.println("Finish setup");
    }

    if(inputvalue ==  'u'){
        go_to_pos_end(250, 0, 58, 1);
    }

    if(inputvalue == 'h'){
        go_to_pos_end(210, 0, 89, 0);
        go_to_pos_end(180, 0, 60, 1);
    }
    if(inputvalue == 'b'){
      go_to_pos_end(250, 0, 89, 0);
      int max_val = max(max(b_nums, r_nums), g_nums);
      go_to_pos_end(0, -200, 58 + 40 + max_val * 30, 0);
      if(debug){
        Serial.print("Going to X: 0, Y: -200, "); //drop point
        Serial.println("Z:" + String(60 + b_nums * 30));
      }
      go_to_pos_end(0, -200, 58 + b_nums * 30, 0);
      b_nums += 1;
      Serial.println(b_nums);
      Serial.println("Blue Sorted!");
      delay(1500);
      max_val = max(max(b_nums, r_nums), g_nums);
      go_to_pos_end(0, -200, 58  + max_val * 30, 1);
      rotateS1(0);
    
    }
    if(inputvalue == 'r'){
      go_to_pos_end(250, 0, 89, 0);
      int max_val = max(max(b_nums, r_nums), g_nums);
      go_to_pos_end(75, -200, 58 + 40 + max_val * 30, 0);
      if(debug){
        Serial.println("Going to X: 75, Y: -200, ");
        Serial.println("Z:" + String(60 + r_nums * 30));
      }
      go_to_pos_end(75, -200, 58 + r_nums * 30, 0);
      r_nums += 1;
      Serial.println("Red Sorted!");
      Serial.println(r_nums);
      delay(1500);
      max_val = max(max(b_nums, r_nums), g_nums);
      go_to_pos_end(75, -200, 58 + max_val * 30, 1);
      rotateS1(0);

    }
    if(inputvalue == 'g'){
      go_to_pos_end(250, 0, 89, 0);     // Go up the grab point
      int max_val = max(max(b_nums, r_nums), g_nums);
      go_to_pos_end(150, -200, 58 + 40+ max_val *30, 0);  // higher than drop point
      if(debug){
        Serial.println("Going to X: 150, Y: -200, ");
        Serial.println("Z:" + String(60 + g_nums * 30));
      }
      go_to_pos_end(150, -200, 58 + g_nums *30, 0); // drop point
      g_nums += 1;
      Serial.println("Green Sorted!");
      Serial.println(g_nums);
      delay(1500);
      max_val = max(max(b_nums, r_nums), g_nums);
      go_to_pos_end(150, -200, 58 + max_val *30, 1);  // higher than drop point
      rotateS1(0);
    }

    if(inputvalue == 'w'){
      go_to_pos_end(xyz_current[0] + 1, xyz_current[1], xyz_current[2], 0);
    }
    if(inputvalue == 'a'){
      go_to_pos_end(xyz_current[0] , xyz_current[1] + 1, xyz_current[2], 0);
    }
    if(inputvalue == 's'){
      go_to_pos_end(xyz_current[0] - 1, xyz_current[1], xyz_current[2], 0);
    }
    if(inputvalue == 'd'){
      go_to_pos_end(xyz_current[0], xyz_current[1] - 1, xyz_current[2], 0);
    }
    if(inputvalue == 'q'){
      go_to_pos_end(xyz_current[0], xyz_current[1], xyz_current[2] + 1, 0);
    }
    if(inputvalue == 'e'){
      go_to_pos_end(xyz_current[0], xyz_current[1], xyz_current[2] - 1, 0);
    }

}

void rotateS1(float to_pos) {

  float s1_angle = to_pos - s1_pos;
  Serial.println(s1_pos);
  Serial.println(s1_angle);
  digitalWrite(S1_DIR_PIN, s1_angle ? LOW : HIGH);
  s1_num_steps = round(abs(s1_angle) * STEPS_PER_DEGREE_S1);

  while (s1_num_steps > 0) {
    digitalWrite(S1_STEP_PIN, HIGH);
    delayMicroseconds(s3_delay_us);
    digitalWrite(S1_STEP_PIN, LOW);
    delayMicroseconds(s3_delay_us);
    s1_num_steps--;
  }
  joint_current[0] = to_pos;
  s1_pos = to_pos;
}

