#include <Servo.h>
#include <math.h>


// #define S1_EN_PIN A1
// Based: 1/16, step/angle = 40
#define S1_STEP_PIN 3
#define S1_DIR_PIN 2

// #define S2_EN_PIN 6
// Based: 1/16, step/angle = 40
#define S2_STEP_PIN 5
#define S2_DIR_PIN 4

// S3 1/32 step, ~0.300V
// Neu theo nhu code goc dieu khien: 1/32 buoc va di qua ti le truyen 2/9 thi dong co phai co step/angle la 80
// #define S3_EN_PIN 9
#define S3_STEP_PIN 7
#define S3_DIR_PIN 6

#define S1_STOP_PIN 8
#define S2_STOP_PIN 9
#define S3_STOP_PIN 10

#define SERVO_PIN 11

#define STEPS_PER_DEGREE_S1 40
#define STEPS_PER_DEGREE_S2 40
#define STEPS_PER_DEGREE_S3 80
#define S1_START -7
#define S2_START 132
#define S3_START 0 // home position is -22 degrees compare to horizontal

#define a 75.00
#define b 140.00
#define c 140.00
#define d 130.00

Servo myservo;
int servoAngle = 180;
int servo_open = 160;
int servo_close = 100;

bool s1_stop = true;
float s1_pos = S1_START;
float s1_angel = 0;
uint16_t s1_num_steps = 0;
// uint16_t s1_delay_us = 500;

bool s2_stop = true;
float s2_pos = S2_START;
float s2_angel = 0;
uint16_t s2_num_steps = 0;
// uint16_t s2_delay_us = 1000;

bool s3_stop = true;
float s3_pos = S3_START;
float s3_angel = 0;
uint16_t s3_num_steps = 0;
uint16_t s3_delay_us = 1000;

bool color = false;
float x, y, z, servo_angel = servo_open;
float pre_alpha = 67;

bool debug = true;

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
  myservo.write(servo_close);
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

void calc_pos(float x, float y, float z) {
  float k = pow((sqrt(x * x + y * y) - a), 2) + pow((z - d), 2);
  float phi = degrees(-atan((d - z) / (sqrt(x * x + y * y) - a)) + acos((c * c + k - b * b) / (2 * c * sqrt(k))));
  float alpha = degrees(abs(acos((-c * c - b * b + k) / (2 * c * b))));
  s1_angel = degrees(atan2(y, x)) - s1_pos;
  s1_pos = degrees(atan2(y, x));
  s2_angel = phi - s2_pos;
  s2_pos = phi;
  s3_angel = pre_alpha - (180.00 - alpha - abs(s2_angel));
  // s3_angel = pre_alpha - alpha - s2_angel;

  s3_pos = s3_angel + s3_pos;

  Serial.print("alpha: ");
  Serial.println(alpha);
  Serial.print("S3 Angle: ");
  Serial.print(s3_angel, 2);
  Serial.print(", S3 Pos: ");
  Serial.println(s3_pos, 2);

  Serial.print("S2 Angle: ");
  Serial.print(s2_angel, 2);
  Serial.print(", S2 Pos: ");
  Serial.println(s2_pos, 2);

  Serial.print("S1 Angle: ");
  Serial.print(s1_angel, 2);
  Serial.print(", S1 Pos: ");
  Serial.println(s1_pos, 2);
}

void go_to_pos(float x, float y, float z, uint8_t servo_angel) {
  // Tính động học ngược
  float k = pow((sqrt(x * x + y * y) - a), 2) + pow((z - d), 2);
  float phi = degrees(-atan((d - z) / (sqrt(x * x + y * y) - a)) + acos((c * c + k - b * b) / (2 * c * sqrt(k))));
  float alpha = degrees(abs(acos((-c * c - b * b + k) / (2 * c * b))));
  s1_angel = degrees(atan2(y, x)) - s1_pos;
  s1_pos = degrees(atan2(y, x));
  s2_angel = phi - s2_pos;
  s2_pos = phi;
  s3_angel = pre_alpha - (180.00 - alpha - abs(s2_angel));
  // s3_angel = pre_alpha - alpha - s2_angel;

  s3_pos = s3_angel + s3_pos;

  float diff = abs(abs(s2_pos) - abs(s3_pos));

  // Nếu lệch nhỏ hơn 40
  // if (diff < 50) {
  //   Serial.println("Diff < 50");
  //   s2_angel = s3_pos + 30 - s2_pos;
  //   s2_pos = s3_pos + 30;
  // }

  // Nếu lệch lớn hơn 110
  // else if (diff > 110) {
  //   Serial.println("Diff > 110");
  //   s2_angel = s3_pos + 110 - s2_pos;
  //   s2_pos = s3_pos + 110;
  //   s3_angel = pre_alpha - (180.00 - alpha - s2_angel);
  //   s3_pos += s3_angel;
  // }

// Cập nhật lại góc
  // s2_angel = s2_pos - (phi - s2_angel);
  // s3_angel = pre_alpha - (180.00 - alpha - s2_angel);

  // pre_alpha = alpha;

  // In ra thông tin gỡ lỗi
  if(debug){
    Serial.print("S3 Angle: ");
    Serial.print(s3_angel, 2);
    Serial.print(", S3 Pos: ");
    Serial.println(s3_pos, 2);

    Serial.print("S2 Angle: ");
    Serial.print(s2_angel, 2);
    Serial.print(", S2 Pos: ");
    Serial.println(s2_pos, 2);

    Serial.print("S1 Angle: ");
    Serial.print(s1_angel, 2);
    Serial.print(", S1 Pos: ");
    Serial.println(s1_pos, 2);
  }
  // Xác định chiều quay
  digitalWrite(S1_DIR_PIN, (s1_angel < 0) ? HIGH : LOW); //HIGH == clockwise
  digitalWrite(S2_DIR_PIN, (s2_angel < 0) ? LOW : HIGH);
  digitalWrite(S3_DIR_PIN, (s3_angel < 0) ? LOW : HIGH);

  s1_num_steps = round(abs(s1_angel) * STEPS_PER_DEGREE_S1);
  s2_num_steps = round(abs(s2_angel) * STEPS_PER_DEGREE_S2);
  s3_num_steps = round(abs(s3_angel) * STEPS_PER_DEGREE_S3);

  long max_steps = max(s2_num_steps, s3_num_steps);
  long s2_counter = 0;
  long s3_counter = 0;

  while (s1_num_steps > 0 || s2_num_steps > 0 || s3_num_steps > 0) {
    if (s1_num_steps) digitalWrite(S1_STEP_PIN, HIGH);
    if (s2_num_steps) digitalWrite(S2_STEP_PIN, HIGH);
    if (s3_num_steps) digitalWrite(S3_STEP_PIN, HIGH);
    delayMicroseconds(s3_delay_us); 
    
    if(abs(s2_angel) < abs(s3_angel)){
      if (s3_num_steps) digitalWrite(S3_STEP_PIN, LOW);
      delayMicroseconds(s3_delay_us);
      if (s3_num_steps) s3_num_steps--;
    }
    else {
      if (s2_num_steps) digitalWrite(S2_STEP_PIN, LOW);
      delayMicroseconds(s3_delay_us);
      if (s2_num_steps) s2_num_steps--;
    }

    if (s1_num_steps) digitalWrite(S1_STEP_PIN, LOW);
    if (s2_num_steps) digitalWrite(S2_STEP_PIN, LOW);
    if (s3_num_steps) digitalWrite(S3_STEP_PIN, LOW);
    delayMicroseconds(s3_delay_us);

    if(abs(s2_angel) < abs(s3_angel)){
      if (s3_num_steps) digitalWrite(S3_STEP_PIN, LOW);
      delayMicroseconds(s3_delay_us);
    }
    else{
      if (s2_num_steps) digitalWrite(S2_STEP_PIN, LOW);
      delayMicroseconds(s3_delay_us);
    }

    if (s1_num_steps) s1_num_steps--; 
    if (s2_num_steps) s2_num_steps--;
    if (s3_num_steps) s3_num_steps--; 
  }

  if(debug){
    Serial.println("done!");
    Serial.println("X: " + String(x, 2) + ", Y: " + String(y, 2) + ", Z: " + String(z, 2));
  }
  // Điều khiển servo
  myservo.write(servo_angel);
}


void go_pos(){
  while (!Serial.available()) {}
  float s1_pos_new = Serial.parseFloat();
  Serial.print("s1_pos: ");
  Serial.println(s1_pos_new);
  float s2_pos_new = Serial.parseFloat();
  Serial.print("s2_pos: ");
  Serial.println(s2_pos_new);
  float s3_pos_new = Serial.parseFloat();
  Serial.print("s3_pos: ");
  Serial.println(s3_pos_new);

  s1_angel = s1_pos_new - s1_pos;
  s2_angel = s2_pos_new - s2_pos; 
  s3_angel = s3_pos_new - s3_pos;
  // Serial.print("S3 Angle: ");
  // Serial.print(s3_angel, 2);  // 2 digits after decimal
  // Serial.print(", S3 Pos: ");
  // Serial.println(s3_pos, 2);

  // Serial.print("S2 Angle: ");
  // Serial.print(s2_angel, 2);
  // Serial.print(", S2 Pos: ");
  // Serial.println(s2_pos, 2);

  // Serial.print("S1 Angle: ");
  // Serial.print(s1_angel, 2);
  // Serial.print(", S1 Pos: ");
  // Serial.println(s1_pos, 2);

  //Di chuyển tới vị trí
  if (s1_angel < 0) digitalWrite(S1_DIR_PIN, HIGH);
  else digitalWrite(S1_DIR_PIN, LOW);
  if (s2_angel < 0) digitalWrite(S2_DIR_PIN, LOW);
  else digitalWrite(S2_DIR_PIN, HIGH);
  if (s3_angel < 0) digitalWrite(S3_DIR_PIN, LOW);
  else digitalWrite(S3_DIR_PIN, HIGH);
  s1_num_steps = round(abs(s1_angel) * 40);
  s2_num_steps = round(abs(s2_angel) * 40);
  s3_num_steps = round(abs(s3_angel) * 80);

  while (s1_num_steps || s2_num_steps || s3_num_steps) {
    if (s1_num_steps) digitalWrite(S1_STEP_PIN, HIGH);
    if (s2_num_steps) digitalWrite(S2_STEP_PIN, HIGH);
    if (s3_num_steps) digitalWrite(S3_STEP_PIN, HIGH);
    delayMicroseconds(s3_delay_us); 
    
    if(abs(s2_angel) < abs(s3_angel)){
      if (s3_num_steps) digitalWrite(S3_STEP_PIN, LOW);
      delayMicroseconds(s3_delay_us);
      if (s3_num_steps) s3_num_steps--;
    }
    else {
      if (s2_num_steps) digitalWrite(S2_STEP_PIN, LOW);
      delayMicroseconds(s3_delay_us);
      if (s2_num_steps) s2_num_steps--;
    }

    if (s1_num_steps) digitalWrite(S1_STEP_PIN, LOW);
    if (s2_num_steps) digitalWrite(S2_STEP_PIN, LOW);
    if (s3_num_steps) digitalWrite(S3_STEP_PIN, LOW);
    delayMicroseconds(s3_delay_us);

    if(abs(s2_angel) < abs(s3_angel)){
      if (s3_num_steps) digitalWrite(S3_STEP_PIN, LOW);
      delayMicroseconds(s3_delay_us);
    }
    else{
      if (s2_num_steps) digitalWrite(S2_STEP_PIN, LOW);
      delayMicroseconds(s3_delay_us);
    }

    if (s1_num_steps) s1_num_steps--; 
    if (s2_num_steps) s2_num_steps--;
    if (s3_num_steps) s3_num_steps--; 
  }
  Serial.println("done!");
  
  s1_pos = s1_pos_new;
  s2_pos = s2_pos_new;
  s3_pos = s3_pos_new;

  myservo.write(servo_open);
}

void pick_and_drop() {
  while (!Serial.available()) {}
  x = Serial.parseFloat();
  Serial.print("X: ");
  Serial.println(x);
  y = Serial.parseFloat();
  Serial.print("Y: ");
  Serial.println(y);
  z = Serial.parseFloat();
  Serial.print("Z: ");
  Serial.println(z);
  // color = bool(Serial.parseFloat());
  // if (color) Serial.println("Color: GREEN");
  // else Serial.println("Color: YELLOW");
  // Serial.readStringUntil('\n');

  Serial.println("X: " + String(x, 2) + ", Y: " + String(y, 2) + ", Z: " + String(0, 2));
  go_to_pos(x, y, z, servo_open);
  Serial.println("s1_angel: " + String(s1_angel, 4));
  Serial.println("s2_angel: " + String(s2_angel, 4));
  Serial.println("s3_angel: " + String(s3_angel, 4));

  // Serial.println("X: " + String(x, 2) + ", Y: " + String(y, 2) + ", Z: " + String(z, 2));
  // go_to_pos(x, y, z, 95);
  // Serial.println("s1_angel: " + String(s1_angel, 4));
  // Serial.println("s2_angel: " + String(s2_angel, 4));
  // Serial.println("s3_angel: " + String(s3_angel, 4));

  delay(1000);
  myservo.write(servo_close);
  // Serial.println("X: " + String(x, 2) + ", Y: " + String(y, 2) + ", Z: " + String(0, 2));
  // go_to_pos(x, y, 0, servo_close);
  // Serial.println("s1_angel: " + String(s1_angel, 4));
  // Serial.println("s2_angel: " + String(s2_angel, 4));
  // Serial.println("s3_angel: " + String(s3_angel, 4));

  if (color) {
    Serial.println("X: 0, Y: 60, Z: 50");
    go_to_pos(0, 60, 50, servo_open);
    Serial.println("s1_angel: " + String(s1_angel, 4));
    Serial.println("s2_angel: " + String(s2_angel, 4));
    Serial.println("s3_angel: " + String(s3_angel, 4));
  } else {
    Serial.println("X: 0, Y: 60, Z: 50");
    go_to_pos(0, 60, 50, servo_open);
    Serial.println("s1_angel: " + String(s1_angel, 4));
    Serial.println("s2_angel: " + String(s2_angel, 4));
    Serial.println("s3_angel: " + String(s3_angel, 4));
  }
  Serial.println("Done!");
} 

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
  // // go_to_pos(200, 150, 50, 50);


  // //servo testing
  // myservo.write(servo_open);
  // delay(1000);
  // myservo.write(servo_close);
  // delay(1500);
  // calc_pos(200, 0 , 40);
  go_to_pos(200, 0, 40, servo_open);
}

void loop() {
  // pick_and_drop();
}














//
