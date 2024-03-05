import serial
import time

# List of strings to send
manual_throttle = [f"t{num}\n" for num in range(1060, 1200, 1)]
strings_to_send = ["a\n", *manual_throttle, *manual_throttle[::-1], "s\n"]
delay = 0.05
# manual_throttle = [f"t{num}\n" for num in [1100, 1200, 1100, 1200, 1100, 1200, 1100, 1200, 1100]]
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
    time.sleep(delay)

# Close the serial port
ser.close()
