#include "ArmPi.h"


void setup() {
  Serial.begin(9600);

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
  go_home();  
  // go_to_pos_end(190, 0, 60, 1);
  delay(2000);
  // go_to_pos_end(-40, -200, 60, 1); test xem co vuot qua tam voi khong

  // go_to_pos_end(250, 0, 58, 1);
  // delay(2000);
  // go_to_pos_end(250, 0, 89, 1);

  // delay(2000);
  // go_to_pos_end(-30, -200, 89, 1);
  // delay(2000);
  // go_to_pos_end(-30, -200, 60, 1);
  // delay(2000);
  // go_to_pos_end(-30, -200, 89, 1);
  // delay(2000);
  // // go_to_pos_end(250, 0, 85, 1);
  // delay(2000);
  // go_to_pos_end(190, 0, 60, 1);

  Serial.println("Finish setup");
}

void loop(){
  recvWithEndMarker();
  if (newData) {
    if (isFullCommand) {
      Serial.println("isFullCommand");
      parseData();
      go_to_pos_end(xyz_next[0], xyz_next[1], xyz_next[2], 1);
    } else {
      handleCharCommand(charCommand);
    }
    newData = false;
  }
  // if (Serial.available() > 0) {
  //   char inputvalue = char(Serial.read());

  //   if(inputvalue == '\n' || inputvalue == '\r') return;

  //   if(inputvalue == 'y'){
  //     debug = !debug;
  //   }

  //   if(inputvalue ==  's'){
  //       go_to_pos_end(250, 0, 58, 1);
  //   }
  //   if(inputvalue == 'h'){
  //       go_to_pos_end(210, 0, 89, 0);
  //       go_to_pos_end(190, 0, 60, 1);
  //   }
  //   if(inputvalue == 'b'){
  //     go_to_pos_end(250, 0, 89, 0);
  //     go_to_pos_end(30, -200, 89, 0);
  //     if(debug){
  //       Serial.print("Going to X: 160, Y: -120, ");
  //       Serial.println("Z:" + String(60 * b_nums * 30));
  //     }
  //     go_to_pos_end(160, -120, 60 + b_nums * 30, 0);
  //     b_nums += 1;
  //     Serial.println("Sorted!");
  //     delay(1500);
  //     go_to_pos_end(30, -200, 89, 1);
    
  //   }
  //   if(inputvalue == 'r'){
  //     go_to_pos_end(250, 0, 89, 0);
  //     go_to_pos_end(0, -200, 89, 0);
  //     if(debug){
  //       Serial.println("Going to X: 140, Y: -140, ");
  //       Serial.println("Z:" + String(60 * r_nums * 30));
  //     }
  //     go_to_pos_end(140, -140, 60 * r_nums * 30, 0);
  //     r_nums += 1;
  //     Serial.println("Sorted!");
  //     delay(1500);
  //     go_to_pos_end(0, -200, 89, 1);
      
  //   }
  //   if(inputvalue == 'g'){
  //     go_to_pos_end(250, 0, 89, 0);
  //     go_to_pos_end(-30, -200, 89, 0);
  //     if(debug){
  //       Serial.println("Going to X: 120, Y: -160, ");
  //       Serial.println("Z:" + String(60 * g_nums * 30));
  //     }
  //     go_to_pos_end(120, -160, 60 * g_nums *30, 0);
  //     g_nums += 1;
  //     Serial.println("Sorted!");
  //     delay(1500);
  //     go_to_pos_end(-30, -200, 89, 1);
    
  //   }
  // }
}













//
