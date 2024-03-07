# DRIFT

## Arduino setup

Install the following libraries:

```
Servo
RC_ESC
```

Then, open `drift.ino`, compile it, and upload it to the board.

To see what is going on and send inputs manually, open the Serial Monitor (baud rate `115200`)

## Python setup

Create a virtual environment with pip, then activate it:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the required packages (make sure the virtualenv is active!):

```bash
pip install -r requirements.txt
```

Then, run the script:

```bash
python control.py
```

## Running

**IMPORTANT**: When the Arduino board writes to serial, you MUST read it as soon as possible. If you don't, the Arduino will most likely not execute commands as expected. This is due to the way `Serial.available()` (at the beginning of the loop in `drift.ino`) works.

There are a few ways to do this:

- Using the Serial Monitor in the Arduino IDE or VSCode
  - This works fine, because serial output is always being read. The ESC will never actually go to the "inactive".
  - This should work well on all operating systems
  - NOTE: if you want to manually send commands to the Arduino from the serial monitor, make sure you select `LF` **line endings**. This will allow the Arduino to read and execute your command immediately, instead of waiting for the `Serial.readStringUntil()` function to time out
- Using the `tail -f /dev/ttyACM0 -s 0.001` command in a terminal
  - Very useful for logging directly to a file: `tail -f /dev/ttyACM0 -s 0.001 >> run.log`
  - This also works fine, as long as you specify a fast refresh interval (`-s 0.001` will refresh every ~1ms). If you don't, and the Arduino starts spamming messages (eg. when reading throttle from the potentiometer), you might not be able to send another command until you stop `tail` (because the Arduino will always be too busy writing?). If the Arduino is not spamming, even the default interval (1s) is fine
  - Note: this assumes that the Arduino is connected to the `/dev/ttyACM0` port on Linux/MacOS. TODO: figure out Windows
- Using the `ser.readline()` function directly in the python script
  - DO NOT USE THIS, it seems unreliable? (Not sure why - [check docs](https://pyserial.readthedocs.io/en/latest/shortintro.html#readline)) 
  - This kinda works sometimes, but if the ESC is in the "inactive" state (single beep every 2-3 seconds), the script might NOT "wake up" the ESC in time - especially if it immediately starts sending commands.
  - TODO: check out `serial.tools.miniterm`
  - TODO: try opening the serial connection as a file, and use regular read/write operations?
  
You can also manually send commands from a terminal like this: `echo "t1000" > /dev/ttyACM0` (this will set the throttle to 1000). Note that this command only *writes* to serial, so you still nead something to read the serial response (either in another terminal, or the Serial Monitor in VSCode/Arduino IDE).