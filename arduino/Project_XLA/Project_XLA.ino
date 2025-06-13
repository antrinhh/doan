#include "ArmPi.h"

void setup() {
  Serial.begin(9600);

  myservo.detach();

  // pinMode(S1_EN_PIN, OUTPUT);
  pinMode(S1_STEP_PIN, OUTPUT);
  pinMode(S1_DIR_PIN, OUTPUT);
  // pinMode(S2_EN_PIN, OUTPUT);
  pinMode(S2_STEP_PIN, OUTPUT);
  pinMode(S2_DIR_PIN, OUTPUT);
  // pinMode(S3_EN_PIN, OUTPUT);
  pinMode(S3_STEP_PIN, OUTPUT);
  pinMode(S3_DIR_PIN, OUTPUT);
  pinMode(S1_STOP_PIN, INPUT_PULLUP);
  pinMode(S2_STOP_PIN, INPUT_PULLUP);
  pinMode(S3_STOP_PIN, INPUT_PULLUP);

  myservo.attach(SERVO_PIN, 550, 2420);

  myservo.write(SERVO_CLOSE);
  myservo.write(SERVO_OPEN);
  myservo.write(SERVO_CLOSE);
  go_home();  

  go_to_pos_end(180, 0, 66, 1);
  delay(2000);
  Serial.println("Finish setup");
}

void loop(){
  if (Serial.available() > 0) {
    char inputvalue = char(Serial.read());

    if (inputvalue == '\n' || inputvalue == '\r') return;

    if(inputvalue ==  's'){
        go_to_pos_end(290, 0, 80, 1);
    }
    if(inputvalue == 'h'){
        go_to_pos_end(180, 0, 66, 1);
    }
    if(inputvalue == 'b'){
      Serial.println("X: 100, Y: 200, Z: 50");
      go_to_pos_end(100, -200, 78, 1);
      Serial.println("s1_angle: " + String(s1_angle, 4));
      Serial.println("s2_angle: " + String(s2_angle, 4));
      Serial.println("s3_angle: " + String(s3_angle, 4));
    }
    if(inputvalue == 'r'){
      Serial.println("X: 0, Y: 200, Z: 50");
      go_to_pos_end(0, -200, 78, 1);
      Serial.println("s1_angle: " + String(s1_angle, 4));
      Serial.println("s2_angle: " + String(s2_angle, 4));
      Serial.println("s3_angle: " + String(s3_angle, 4));
    }
    if(inputvalue == 'g'){
      Serial.println("X: -200, Y: 200, Z: 50");
      go_to_pos_end(-100, -200, 78, 1);
      Serial.println("s1_angle: " + String(s1_angle, 4));
      Serial.println("s2_angle: " + String(s2_angle, 4));
      Serial.println("s3_angle: " + String(s3_angle, 4));
    }
}













//
