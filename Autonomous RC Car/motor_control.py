# motor_control.py — Testing version with print output for direct speed changes

current_speed = 100  # Default speed

def _set_direction(left_in1, left_in2, right_in1, right_in2):
    pass

def _set_speed(left_speed_pct, right_speed_pct):
    pass  # Skip real output here to avoid duplicates

def set_speed(speed_pct):
    global current_speed
    current_speed = speed_pct
    print(f"speed to {speed_pct}%")

def stop():
    print("stop")
    _set_direction(0, 0, 0, 0)
    _set_speed(0, 0)

def move_forward(speed_pct=None):
    if speed_pct is None:
        speed_pct = current_speed
    print(f"forward at {speed_pct}%")
    _set_direction(1, 0, 1, 0)
    _set_speed(speed_pct, speed_pct)

def move_backward(speed_pct=None):
    if speed_pct is None:
        speed_pct = current_speed
    print(f"backward at {speed_pct}%")
    _set_direction(0, 1, 0, 1)
    _set_speed(speed_pct, speed_pct)

def rotate_left(speed_pct=None):
    if speed_pct is None:
        speed_pct = current_speed
    print(f"left at {speed_pct}%")
    _set_direction(0, 1, 1, 0)
    _set_speed(speed_pct, speed_pct)

def rotate_right(speed_pct=None):
    if speed_pct is None:
        speed_pct = current_speed
    print(f"right at {speed_pct}%")
    _set_direction(1, 0, 0, 1)
    _set_speed(speed_pct, speed_pct)