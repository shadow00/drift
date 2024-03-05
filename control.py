import serial
import time

# List of strings to send
manual_throttle = [f"t{num}\n" for num in range(1060, 1200, 1)]
strings_to_send = ["a\n", *manual_throttle, *manual_throttle[::-1], "s\n"]
delay = 0.05
# manual_throttle = [f"t{num}\n" for num in [1100, 1200, 1100, 1200, 1100, 1200, 1100, 1200, 1100]]
# strings_to_send = ["a\n", "e7\n", "a\n", *manual_throttle, "s\n"]
# strings_to_send = ["a\n", *manual_throttle, "s\n"]
# delay = 0.1

# Open the serial port
# Replace '/dev/ttyACM0' with the actual port name if different
# Adjust the baud rate (e.g., 9600, 115200) as necessary
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

# Write each string in the list to the serial port
for string in strings_to_send:
    print(f"Sending: {string.rstrip()}")
    ser.write(string.encode('ascii'))
    # WARNING: You MUST read the serial output from the Arduino if you want
    # it to actually execute what you told it to do!
    # Either read the lines from here (don't need to print them out though),
    # OR open the serial monitor in the Arduino IDE/vscode/tty emulator/whatever
    # BUT NEVER OPEN TWO READERS AT THE SAME TIME
    resp = ser.readline()
    print(resp.decode('ascii').rstrip())
    time.sleep(delay)

# Close the serial port
ser.close()
