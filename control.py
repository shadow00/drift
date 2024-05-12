import serial
import signal
import sys
import time

def signal_handler(signal, frame):
    global ser
    print('Shutting down, sending STOP command')
    ser.write("s\n".encode('ascii'))
    resp = ser.readline()
    print(resp)
    # ser.write("s\n".encode('ascii'))
    # ser.write("s\n".encode('ascii'))
    print('Done')
    ser.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def since(t0):
    t = time.time()
    dt = t - t0
    ts = f"{dt:.6f}"
    return ts

# List of strings to send
arm_delay = 1
# manual_throttle = [f"t{num}" for num in range(1100, 1300, 2)]  # Smooth ramp
manual_throttle = [f"t{num}" for num in range(1100, 1801, 50)]  # Small steps (18)
# strings_to_send = ["a", *manual_throttle, *manual_throttle[::-1], "s"]
strings_to_send = ["a", f"D{arm_delay}", *manual_throttle, *manual_throttle[::-1], "s"]
# delay = 0.2
# manual_throttle = [f"t{num}" for num in [1100, 1200, 1100, 1200, 1100, 1200, 1100, 1200, 1100]]
# # strings_to_send = ["a\n", "e7\n", "a\n", *manual_throttle, "s\n"]
# strings_to_send = ["a", *manual_throttle, "s"]
# # delay = 0.001
# delay = 0.01  # Smooth ramp
delay = 0.5  # Small steps

expected_time = sum([int(s[1:]) if s[0]=="D" else delay for s in strings_to_send])

# Open the serial port
# Replace '/dev/ttyACM0' with the actual port name if different
# Adjust the baud rate (e.g., 9600, 115200) as necessary
# ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.1)
ser = serial.Serial('/dev/ttyACM0')

# stty -F /dev/ttyACM0 raw -iexten -echo -echoe -echok -echoctl -echoke -onlcr
# stty -F /dev/ttyACM0 cs8 9600 ignbrk -brkint -imaxbel -opost -onlcr -isig -icanon -iexten -echo -echoe -echok -echoctl -echoke noflsh -ixon -crtscts
# tail -f /dev/ttyACM0 -s 0.0001 >> test_format5.txt
print(f"Sequence will take ~{expected_time:.1f}s for {len(strings_to_send)} commands")

t0 = time.time()
# time.sleep(0.6)
# ready = ser.readline()
# print(f"{since(t0)} - {ready}")

# Write each string in the list to the serial port
for string in strings_to_send:
    start = time.time()
    if string[0] == "D":  # Use the "D" command to set a delay (in seconds!) in the loop
        D = int(string[1:])
        print(f"{since(t0)} - Delaying for {D}s")
        time.sleep(D)
        continue
    print(f"{since(t0)} - Sending: {string.rstrip()}")
    string = string + "\n" # Always append a newline, to prevent the serial read from going into timeout and get a faster response time
    ser.write(string.encode('ascii'))
    print(f"{since(t0)} - Sent: {string.rstrip()}")
    # ser.flush()
    # WARNING: You MUST read the serial output from the Arduino if you want
    # it to actually execute what you told it to do!
    # Either read the lines from here (don't need to print them out though),
    # OR open the serial monitor in the Arduino IDE/vscode/tty emulator/whatever
    # BUT NEVER OPEN TWO READERS AT THE SAME TIME
    # time.sleep(0.01)
    # if ser.in_waiting > 0:
    # resp = ser.readline()
    # print(f"{since(t0)} -", resp.decode('ascii').rstrip())
    # resp = ser.readlines()
    # for l in resp:
    #     print(f"{since(t0)} -", l.decode('ascii').rstrip())
    # resp = ser.read_until('\n')
    # Sending messages and reading the response takes some time, it makes the timing less accurate
    now = time.time()
    if delay - (now - start) > 0:
        time.sleep(delay - (now - start))
    else:
        print(f"{since(start)} - WARNING: loop took {now - start}s, longer than desired delay {delay}s")
    start = now

# Close the serial port
ser.close()
