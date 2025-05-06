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
  go_home();


  go_to_pos_end(200, 0, 40, 1);
  Serial.println("Finish setup");
}

void loop() {
  recvWithEndMarker();
  if (newData) {
    parseData();
    newData = false;
    pick_and_drop();
  }
}













//
