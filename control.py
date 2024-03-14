import serial
import time

class Arduino:
    def __init__(self, serialPortName, baudRate, timeout=1):
        self.startMarker = '<'
        self.endMarker = '>'
        self.dataBuf = ""
        self.dataStarted = False
        self.messageComplete = False
        # self.serialPort = serial.Serial(port=serialPortName, baudrate=baudRate, timeout=timeout, rtscts=True)
        self.serialPort = serial.Serial(port=serialPortName, baudrate=baudRate, timeout=timeout)

    def send(self, msg):
        # Add the start- and end-markers before sending
        stringWithMarkers = f"{self.startMarker}{msg}{self.endMarker}"
        self.serialPort.write(stringWithMarkers.encode('utf-8')) # encode needed for Python3

    def readline(self):
        msg = self.serialPort.readline().decode("utf-8").rstrip()
        return msg

    def readlines(self):
        if self.serialPort.inWaiting() > 0:
            msgs = self.serialPort.readlines()
            return msgs
        else:
            return []

    def recv(self):
        while self.serialPort.inWaiting() > 0 and self.messageComplete == False:
            x = self.serialPort.read().decode("ascii") # decode needed for Python3
            
            if self.dataStarted == True:
                if x != self.endMarker:
                    self.dataBuf = self.dataBuf + x
                else:
                    self.dataStarted = False
                    self.messageComplete = True
            elif x == self.startMarker:
                self.dataBuf = ''
                self.dataStarted = True
        
        if (self.messageComplete == True):
            self.messageComplete = False
            return self.dataBuf
        else:
            return "XXX" 

    def flushOutput(self):
        self.serialPort.flushOutput()

    def close(self):
        self.serialPort.close()

# List of strings to send
manual_throttle = [f"t{num}" for num in range(1060, 1200, 1)]
strings_to_send = ["a", *manual_throttle, *manual_throttle[::-1], "s"]
delay = 0.05
# manual_throttle = [f"t{num}" for num in [1100, 1200, 1100, 1200, 1100, 1200, 1100, 1200, 1100]]
# strings_to_send = ["a", *manual_throttle, "s"]
# delay = 0.1

# Open the serial port
# Replace '/dev/ttyACM0' with the actual port name if different
# Adjust the baud rate (e.g., 9600, 115200) as necessary
ser = Arduino('/dev/ttyACM0', 115200, timeout=0.1)
t0 = time.time()
time.sleep(0.6)
ready = ser.recv()
print(f"{since(t0)} - {ready}")

# Write each string in the list to the serial port
for string in strings_to_send:
    print(f"{since(t0)} - Sending: {string.rstrip()}")
    ser.send(string)
    print(f"{since(t0)} - Sent: {string.rstrip()}")
    # WARNING: You MUST read the serial output from the Arduino if you want
    # it to actually execute what you told it to do!
    # Either read the lines from here (don't need to print them out though),
    # OR open the serial monitor in the Arduino IDE/vscode/tty emulator/whatever
    # BUT NEVER OPEN TWO READERS AT THE SAME TIME
    resp = ser.recv()
    print(f"{since(t0)} -", resp.rstrip())
    time.sleep(delay)

# Close the serial port
ser.close()
