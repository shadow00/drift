#include "ESC.h"

unsigned int ESCpin = 7;
unsigned int POTpin;
unsigned int pot_value;
unsigned int throttle = 0;

#define SPEED_MIN (1060) // Set the Minimum Speed in microseconds
#define SPEED_MAX (1860) // Set the Minimum Speed in microseconds
#define ARM_VAL (500) // Set the Arm Value in microseconds

ESC myESC(ESCpin, SPEED_MIN, SPEED_MAX, ARM_VAL); // ESC_Name (PIN, Minimum Value, Maximum Value, Arm Value)

String command;
const char arm_command = 'a';
const char thr_command = 't';
const char pot_command = 'p';
const char stop_command = 's';
const char calib_command = 'c';
const char escpin_command = 'e';
const char nothing_to_do = (char)0;
char cmd = nothing_to_do;  // Default command on first start

void setup() {
  Serial.begin(115200);  // opens serial port, sets data rate to 9600 bps
  Serial.setTimeout(10);  // Set timeout to 10ms to waste less time when reading serial input
}

void loop() {  
  while (Serial.available() == 0) {
    switch (cmd)
    {
    case arm_command:
      myESC.arm(); // Send the Arm value
      Serial.println("Sending ARM command");
      cmd = nothing_to_do;
      break;
    case thr_command:
      Serial.print("Set throttle to ");
      Serial.println(throttle);
      myESC.speed(throttle); // sets the ESC speed according to the scaled value
      cmd = nothing_to_do;
      break;
    case pot_command:
      pot_value = analogRead(POTpin);
      throttle = map(pot_value, 0, 1023, SPEED_MIN, SPEED_MAX);
      Serial.print("Reading pin ");
      Serial.print(POTpin);
      Serial.print(" - Set throttle to ");
      Serial.println(throttle);
      myESC.speed(throttle); // sets the ESC speed according to the scaled value
      break;
    case stop_command:
      myESC.stop(); // Send the Stop value
      Serial.println("Sending STOP command");
      cmd = nothing_to_do;
      break;
    case calib_command:
      myESC.calib(); // Calibrate
      Serial.println("Throttle calibration");
      // cmd = arm_command; // Arm after calibration?
      cmd = nothing_to_do;
      break;
    case escpin_command:
      if (ESCpin > 1 && ESCpin <= NUM_DIGITAL_PINS) {
        Serial.print("Setting ESC to pin ");
        Serial.println(ESCpin);
        cmd = nothing_to_do;
      } else {
        Serial.print("WARNING: Invalid ESC pin ");
        Serial.println(ESCpin);
        cmd = nothing_to_do;
      }
      break;
    case nothing_to_do:
      // Serial.println("Nothing to do");
      break;
    default:
      Serial.print("Unrecognized command! cmd = '");
      Serial.print(cmd);
      Serial.println("' - doing nothing");
      break;
    }
    delay(5);
  }

  command = Serial.readStringUntil('\n'); // Note: the '\n' character is discarded from the serial buffer
  command.trim();
  unsigned int cmdlen = command.length();
  cmd = command.charAt(0);  // Warning: this limits the commands to a single character (one byte)

  // Warning: this matches the beginning of the string - there are no safety checks for what comes after!
  // Eg. by typing "as", this will match the arm command "a", becaues the input starts with "a"
  if (command.startsWith(String(arm_command))) {
    // cmd = arm_command;
  } else if (command.startsWith(String(thr_command))) {
    if (cmdlen > 1 && cmdlen < 6) { // match "t0" - "t1024"
      throttle = command.substring(1).toInt();
    }
    // cmd = thr_command;
  } else if (command.startsWith(String(pot_command))) {
    // "pa0"
    if (cmdlen > 1) {
      String pot_str = command.substring(1);  // Assume there is no space after the 'p'
      pot_str.toLowerCase();
      // // if (pot_str.startsWith("a") && isDigit(pot_str.substring(1))) {}
      // if (pot_str.startsWith("a") && pot_str.substring(1).toInt()) {
      if (pot_str.startsWith("a")) {
        // Analog pins "a0" - "a7" for stuff like Arduino Uno, or "a11" for the Arduino Giga R1
        // https://github.com/arduino/ArduinoCore-avr/blob/master/variants/standard/pins_arduino.h#L28-L72
        // https://github.com/arduino/ArduinoCore-mbed/blob/main/variants/GIGA/pins_arduino.h#L21-L56
        int analog_pin_num = pot_str.substring(1).toInt();
        POTpin = NUM_DIGITAL_PINS - NUM_ANALOG_INPUTS + analog_pin_num;
      } else if (isDigit(pot_str[0])) {
        POTpin = pot_str.substring(0).toInt();
      }
    }
    // cmd = pot_command;
  } else if (command.startsWith(String(stop_command))) {
    // cmd = stop_command;
  } else if (command.startsWith(String(calib_command))) {
    // cmd = calib_command;
  } else if (command.startsWith(String(escpin_command))) {
    // myESC.~ESC();
    // Warning: no error checking. If the string is invalid, this will return 0
    // and it will be rejected in the loop
    ESCpin = command.substring(1).toInt();
    myESC = ESC(ESCpin, SPEED_MIN, SPEED_MAX, ARM_VAL); // ESC_Name (PIN, Minimum Value, Maximum Value, Arm Value)
  } else {
    // cmd = wrong_command;
  }
}
