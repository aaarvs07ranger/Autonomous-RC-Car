import lgpio
import time

# GPIO pin assignments (BCM numbering)
LEFT_IN1   = 17  # Pin 11
LEFT_IN2   = 27  # Pin 13
RIGHT_IN1  = 22  # Pin 15
RIGHT_IN2  = 23  # Pin 16
LEFT_PWM   = 18  # Pin 12 (PWM0)
RIGHT_PWM  = 13  # Pin 33 (PWM1)

# PWM configuration
PWM_FREQ_HZ     = 1000       # 1 kHz PWM frequency
MAX_DUTY_CYCLE  = 1000000    # lgpio uses a 0…1 000 000 range for duty cycle

# Open a handle to GPIO chip 0
h = lgpio.gpiochip_open(0)

# Claim the four direction pins as outputs
for pin in (LEFT_IN1, LEFT_IN2, RIGHT_IN1, RIGHT_IN2):
    lgpio.gpio_claim_output(h, pin)

# Claim the two PWM pins
# Note: lgpio provides gpio_claim_pwm() to claim PWM on a GPIO
lgpio.gpio_claim_pwm(h, LEFT_PWM)
lgpio.gpio_claim_pwm(h, RIGHT_PWM)

def _set_direction(left_in1, left_in2, right_in1, right_in2):
    """
    Internal helper: sets the four direction pins HIGH/LOW.
    """
    lgpio.gpio_write(h, LEFT_IN1,  left_in1)
    lgpio.gpio_write(h, LEFT_IN2,  left_in2)
    lgpio.gpio_write(h, RIGHT_IN1, right_in1)
    lgpio.gpio_write(h, RIGHT_IN2, right_in2)

def _set_speed(left_speed_pct, right_speed_pct):
    """
    Internal helper: sets PWM duty‐cycle on LEFT_PWM / RIGHT_PWM based on a percentage.
    left_speed_pct, right_speed_pct: 0…100 (integers)
    """
    # Clamp to 0…100
    left_speed_pct  = max(0, min(100, left_speed_pct))
    right_speed_pct = max(0, min(100, right_speed_pct))

    # Convert percentage to lgpio duty-cycle range (0…1 000 000)
    left_duty  = int(left_speed_pct  * (MAX_DUTY_CYCLE / 100))
    right_duty = int(right_speed_pct * (MAX_DUTY_CYCLE / 100))

    # Start (or update) PWM on each pin
    # Note: gpio_pwm(handle, gpio, frequency, dutycycle)
    lgpio.gpio_pwm(h, LEFT_PWM,  PWM_FREQ_HZ,  left_duty)
    lgpio.gpio_pwm(h, RIGHT_PWM, PWM_FREQ_HZ, right_duty)

def stop():
    """
    Fully stop both motors: set direction pins LOW and PWM duty to 0.
    """
    _set_direction(0, 0, 0, 0)
    _set_speed(0, 0)

def move_forward(speed_pct=100):
    """
    Drive both motors forward at speed_pct (0…100).
    """
    # Forward = IN1 = 1, IN2 = 0 for each motor
    _set_direction(1, 0, 1, 0)
    _set_speed(speed_pct, speed_pct)

def move_backward(speed_pct=100):
    """
    Drive both motors backward at speed_pct (0…100).
    """
    # Backward = IN1 = 0, IN2 = 1 for each motor
    _set_direction(0, 1, 0, 1)
    _set_speed(speed_pct, speed_pct)

def rotate_left(speed_pct=100):
    """
    Rotate left in place: left motor backward, right motor forward.
    """
    # Left motor backward = IN1=0, IN2=1; Right motor forward = IN1=1, IN2=0
    _set_direction(0, 1, 1, 0)
    _set_speed(speed_pct, speed_pct)

def rotate_right(speed_pct=100):
    """
    Rotate right in place: left motor forward, right motor backward.
    """
    _set_direction(1, 0, 0, 1)
    _set_speed(speed_pct, speed_pct)