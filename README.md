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