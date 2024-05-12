#undef HID_ENABLED
#include <DueAdcFast.h>
#include "ESC.h"

#define mySerial SerialUSB

DueAdcFast DueAdcF(1024);  // 1024 measures is dimension of internal buffer. (min is 1024)

#define SAMPLES (1) // Max ticks to count within a sampling interval
volatile unsigned long results[SAMPLES][5] = {0};
volatile unsigned long times[SAMPLES][5] = {0};

unsigned int ESCpin = 9;
unsigned int POTpin;  // DEFAULT POT PIN TO A5
unsigned int pot_value;
unsigned int load_value;
unsigned int now;
unsigned int throttle = 0;
unsigned long start = 0;
unsigned long stop = 0;

// #define SPEED_MIN (1060) // Set the Minimum Speed in microseconds
// #define SPEED_MAX (1860) // Set the Minimum Speed in microseconds
// #define ARM_VAL (500) // Set the Arm Value in microseconds
#define SPEED_MIN (1100) // Set the Minimum Speed in microseconds
#define SPEED_MAX (2000) // Set the Minimum Speed in microseconds
#define ARM_VAL (1000) // Set the Arm Value in microseconds

ESC myESC(ESCpin, SPEED_MIN, SPEED_MAX, ARM_VAL); // ESC_Name (PIN, Minimum Value, Maximum Value, Arm Value)

String command;
const char arm_command = 'a';
const char thr_command = 't';
const char pot_command = 'p';
const char load_command = 'l';
const char stop_command = 's';
const char calib_command = 'c';
const char escpin_command = 'e';
const char nothing_to_do = (char)0;
char cmd = nothing_to_do;  // Default command on first start
bool print_thr = true;
String thr_str;
String pot_str;


// these 3 lines of code are essential for the functioning of the library
// you don't call ADC_Handler.
// is used automatically by the PDC every time it has filled the buffer
// and rewrite buffer.
void ADC_Handler() {
  DueAdcF.adcHandler();
}

void mydelay(unsigned long interval){
    unsigned int a = micros();
    unsigned int b = micros();
    while (b - a < interval) {
        b = micros();
    }
}

void measure_and_print_rpm() {
  for (int i=0; i<SAMPLES; i++) {
    times[i][0] = micros();
    results[i][0] = DueAdcF.ReadAnalogPin(A0); // Load cell
    times[i][1] = micros();
    results[i][1] = DueAdcF.ReadAnalogPin(A1);
    times[i][2] = micros();
    results[i][2] = DueAdcF.ReadAnalogPin(A2);
    times[i][3] = micros();
    results[i][3] = DueAdcF.ReadAnalogPin(A3);
    times[i][4] = micros();
    results[i][4] = DueAdcF.ReadAnalogPin(A4);
    mydelay(100);
  }
  for (int i=0; i<SAMPLES; i++) {
  mySerial.print(throttle);
  mySerial.print(',');
    mySerial.print(times[i][1]);
  mySerial.print(',');
    mySerial.print(results[i][1]);
  mySerial.print(',');
    mySerial.print(times[i][2]);
  mySerial.print(',');
    mySerial.print(results[i][2]);
  mySerial.print(',');
  mySerial.print(times[i][3]);
  mySerial.print(',');
  mySerial.print(results[i][3]);
  mySerial.print(',');
  mySerial.print(times[i][4]);
  mySerial.print(',');
  mySerial.print(results[i][4]);
  mySerial.print(',');
  mySerial.print(times[i][0]); // Load cell
  mySerial.print(',');
  mySerial.print(results[i][0]); // Load cell
  mySerial.print('\n');
  }
}

void setup() {
  mySerial.begin(115200);  // opens serial port, sets data rate to 115200 bps
  while (!mySerial);  // Wait for serial to initialize
  // mySerial.setTimeout(10);  // Set timeout to 10ms to waste less time when reading serial input
  String rdy = "Arduino is ready! ";
  rdy.concat(millis());
  rdy.concat("ms\n");
  mySerial.print(rdy);
  // https://github.com/AntonioPrevitali/DueAdcFast/blob/main/examples/Sample3/Sample3.pde
  // analogReadResolution(12);
  DueAdcF.EnablePin(A0);  // Load cell
  DueAdcF.EnablePin(A1);  // Neutral point
  DueAdcF.EnablePin(A2);  // Phase 1
  DueAdcF.EnablePin(A3);  // Phase 2
  DueAdcF.EnablePin(A4);  // Phase 3
  DueAdcF.EnablePin(A5);  // Throttle Pot
  DueAdcF.Start1Mhz();       // max speed 1Mhz (sampling rate)
  // DueAdcF.Start(255);        // with prescaler value form 3 to 255.
                             // 255 is approx. 7812 Hz (sampling rate)
}

void loop() {  
  while (mySerial.available() == 0) {
    switch (cmd)
    {
    case arm_command:
      myESC.arm(); // Send the Arm value
      mySerial.println("Sending ARM command");
      cmd = nothing_to_do;
      break;
    case thr_command:
      if (print_thr) {
        thr_str = "Set throttle to ";
        thr_str.concat(throttle);
        thr_str.concat('\n');
        mySerial.print(thr_str);
        print_thr = false;
      }
      myESC.speed(throttle); // sets the ESC speed according to the scaled value
      measure_and_print_rpm();
      // cmd = nothing_to_do;
      break;
    case pot_command:
      // if (print_thr) {
      //   thr_str = "Set throttle to ";
      //   thr_str.concat(throttle);
      //   thr_str.concat('\n');
      //   mySerial.print(thr_str);
      //   print_thr = false;
      // }
      pot_value = DueAdcF.ReadAnalogPin(POTpin);
      throttle = map(pot_value, 0, 4096, SPEED_MIN, SPEED_MAX);
      // throttle = map(pot_value, 0, 4096, SPEED_MIN, 1300); // Limit throttle
      // throttle = 1150;
      // pot_str = "Pin ";
      // pot_str.concat(POTpin);
      // pot_str.concat(" - Set throttle to ");
      // pot_str.concat(throttle);
      // mySerial.println(pot_str);
      myESC.speed(throttle); // sets the ESC speed according to the scaled value
      measure_and_print_rpm();
      break;
    case load_command:
      if (print_thr) {
        mySerial.print("Reading LOAD CELL\n");
        print_thr = false;
      }
      now = micros();
      load_value = DueAdcF.ReadAnalogPin(A0);  // Load Cell
      mySerial.print(now);
      mySerial.print(',');
      mySerial.print(load_value);
      mySerial.print('\n');
      break;
    case stop_command:
      myESC.stop(); // Send the Stop value
      mySerial.println("Sending STOP command");
      cmd = nothing_to_do;
      break;
    case calib_command:
      myESC.calib(); // Calibrate
      mySerial.println("Throttle calibration");
      // cmd = arm_command; // Arm after calibration?
      cmd = nothing_to_do;
      break;
    case escpin_command:
      if (ESCpin > 1 && ESCpin <= NUM_DIGITAL_PINS) {
        mySerial.print("Setting ESC to pin ");
        mySerial.println(ESCpin);
        cmd = nothing_to_do;
      } else {
        mySerial.print("WARNING: Invalid ESC pin ");
        mySerial.println(ESCpin);
        cmd = nothing_to_do;
      }
      break;
    case nothing_to_do:
      if (print_thr) {
        mySerial.println("Nothing to do");
        print_thr = false;
      }
      break;
    default:
      String resp = "Unrecognized command, doing nothing! cmd = '";
      resp.concat(command);
      mySerial.println(resp);
      break;
    }
    // delay(5);
  }

  command = mySerial.readStringUntil('\n'); // Note: the '\n' character is discarded from the serial buffer
  command.trim();
  unsigned int cmdlen = command.length();
  cmd = command.charAt(0);  // Warning: this limits the commands to a single character (one byte)

  // Warning: this matches the beginning of the string - there are no safety checks for what comes after!
  // Eg. by typing "as", this will match the arm command "a", becaues the input starts with "a"
  if (command.startsWith(String(arm_command))) {
    // cmd = arm_command;
  } else if (command.startsWith(String(thr_command))) {
    print_thr = true;
    if (cmdlen > 1 && cmdlen < 6) { // match "t0" - "t1024"
      throttle = command.substring(1).toInt();
    } else {
      cmd = nothing_to_do;
    }
    // cmd = thr_command;
  } else if (command.startsWith(String(pot_command))) {
    // print_thr = true;
    POTpin = A5; // DEFAULT POT PIN TO A5
    // "pa0"
    // if (cmdlen > 1) {
    //   String pot_str = command.substring(1);  // Assume there is no space after the 'p'
    //   pot_str.toLowerCase();
    //   // // if (pot_str.startsWith("a") && isDigit(pot_str.substring(1))) {}
    //   // if (pot_str.startsWith("a") && pot_str.substring(1).toInt()) {
    //   if (pot_str.startsWith("a")) {
    //     // Analog pins "a0" - "a7" for stuff like Arduino Uno, or "a11" for the Arduino Giga R1
    //     // https://github.com/arduino/ArduinoCore-avr/blob/master/variants/standard/pins_arduino.h#L28-L72
    //     // https://github.com/arduino/ArduinoCore-mbed/blob/main/variants/GIGA/pins_arduino.h#L21-L56
    //     int analog_pin_num = pot_str.substring(1).toInt();
    //     POTpin = NUM_DIGITAL_PINS - NUM_ANALOG_INPUTS + analog_pin_num;
    //   } else if (isDigit(pot_str[0])) {
    //     POTpin = pot_str.substring(0).toInt();
    //   }
    // } else {
    //   POTpin = A5; // DEFAULT POT PIN TO A5
    // }
    // cmd = pot_command;
  } else if (command.startsWith(String(load_command))) {
    print_thr = false;
    // cmd = load_command;
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
