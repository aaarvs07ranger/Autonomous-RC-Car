from flask import Flask, render_template, Response, request
import cv2
import motor_control
import mediapipe as mp
import time

app = Flask(__name__)
camera = cv2.VideoCapture(0)  # Use the first webcam

# MediaPipe setup for hand tracking
mp_hands = mp.solutions.hands
hands     = mp_hands.Hands(max_num_hands=1)
mp_draw   = mp.solutions.drawing_utils

# Global state for gestures + speed slider
last_action      = None
action_cooldown  = 1.5    # seconds between motor commands to avoid flickering
last_action_time = 0

# Default speed (0–100). Will be updated by the slider whenever a manual button is pressed.
current_speed_pct = 50

def is_palm_open(hand_landmarks):
    tips_ids = [8, 12, 16, 20]
    pip_ids  = [6, 10, 14, 18]

    open_fingers = 0
    for tip, pip in zip(tips_ids, pip_ids):
        tip_y = hand_landmarks.landmark[tip].y
        pip_y = hand_landmarks.landmark[pip].y
        if tip_y < pip_y:
            open_fingers += 1

    thumb_tip_x = hand_landmarks.landmark[4].x
    thumb_ip_x  = hand_landmarks.landmark[3].x
    thumb_open  = thumb_tip_x > thumb_ip_x

    return (open_fingers >= 3) and thumb_open

def is_palm_closed(hand_landmarks):
    tips_ids = [8, 12, 16, 20]
    pip_ids  = [6, 10, 14, 18]

    closed_fingers = 0
    for tip, pip in zip(tips_ids, pip_ids):
        tip_y = hand_landmarks.landmark[tip].y
        pip_y = hand_landmarks.landmark[pip].y
        if tip_y > pip_y:
            closed_fingers += 1

    thumb_tip_x = hand_landmarks.landmark[4].x
    thumb_ip_x  = hand_landmarks.landmark[3].x
    thumb_closed = thumb_tip_x < thumb_ip_x

    return (closed_fingers >= 3) and thumb_closed

def gen_frames():
    global last_action, last_action_time, current_speed_pct

    while True:
        success, frame = camera.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb_frame)

        if result.multi_hand_landmarks:
            hand_landmarks = result.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            now = time.time()
            if now - last_action_time > action_cooldown:
                speed = current_speed_pct

                if is_palm_open(hand_landmarks):
                    if last_action != 'forward':
                        motor_control.move_forward(speed)
                        last_action = 'forward'
                        last_action_time = now

                elif is_palm_closed(hand_landmarks):
                    if last_action != 'stop':
                        motor_control.stop()
                        last_action = 'stop'
                        last_action_time = now

        else:
            now = time.time()
            if now - last_action_time > action_cooldown:
                if last_action != 'stop':
                    motor_control.stop()
                    last_action = 'stop'
                    last_action_time = now

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html', speed=current_speed_pct)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/move', methods=['POST'])
def move():
    global current_speed_pct

    direction = request.form.get('direction', 'stop')
    try:
        speed = int(request.form.get('speed', 50))
    except ValueError:
        speed = 50

    speed = max(0, min(100, speed))

    # If the speed changed, print it first
    if speed != current_speed_pct:
        motor_control.set_speed(speed)

    current_speed_pct = speed

    if direction == 'forward':
        motor_control.move_forward(speed)
    elif direction == 'backward':
        motor_control.move_backward(speed)
    elif direction == 'left':
        motor_control.rotate_left(speed)
    elif direction == 'right':
        motor_control.rotate_right(speed)
    else:
        motor_control.stop()

    return ('', 204)

@app.route('/speed', methods=['POST'])
def speed():
    """
    Separate route for adjusting only speed from slider.
    Calls set_speed() to ensure console feedback.
    """
    global current_speed_pct
    try:
        new_speed = int(request.form.get('speed', 50))
    except ValueError:
        new_speed = 50

    new_speed = max(0, min(100, new_speed))
    if new_speed != current_speed_pct:
        motor_control.set_speed(new_speed)
    current_speed_pct = new_speed

    return ('', 204)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)