#include "ESC.h"

int ESCpin = 7;
int POTpin = A0;
unsigned int pot_value;

#define SPEED_MIN (1060) // Set the Minimum Speed in microseconds
#define SPEED_MAX (1860) // Set the Minimum Speed in microseconds
#define ARM_VAL (500) // Set the Arm Value in microseconds

int throttle = ARM_VAL;                           // ARM value
ESC myESC(ESCpin, SPEED_MIN, SPEED_MAX, ARM_VAL); // ESC_Name (PIN, Minimum Value, Maximum Value, Arm Value)
String command;
int cmd = 0;  // Default command on first start
String arm_command = "a";  // 1
String thr_command = "t";  // 2
String stop_command = "s";  // 3
String calib_command = "c";  // 4

void setup() {
  Serial.begin(115200);  // opens serial port, sets data rate to 9600 bps
}

void loop() {  
  while (Serial.available() == 0) {
    switch (cmd)
    {
    case 1:
      myESC.arm(); // Send the Arm value
      Serial.println("Sending ARM command");
      break;
    case 2:
      pot_value = analogRead(POTpin);
      throttle = map(pot_value, 0, 1023, SPEED_MIN, SPEED_MAX);
      Serial.print("Set throttle value to ");
      Serial.println(throttle);
      myESC.speed(throttle); // sets the ESC speed according to the scaled value
      break;
    case 3:
      myESC.stop(); // Send the Stop value
      Serial.println("Sending STOP command");
      break;
    case 4:
      myESC.calib(); // Calibrate
      Serial.println("Throttle calibration");
      cmd = 1; // Arm after calibration
      break;
    default:
      Serial.print("cmd = ");
      Serial.print(cmd);
      Serial.println(" - doing nothing");
      break;
    }
    delay(5);
  }

  command = Serial.readStringUntil('\n');
  command.trim();

  if (command.startsWith(arm_command)) {cmd = 1;}
  else if (command.startsWith(thr_command)) {cmd = 2;}
  else if (command.startsWith(stop_command)) {cmd = 3;}
  else if (command.startsWith(calib_command)) {cmd = 4;}
  else {cmd = 0;}
}
