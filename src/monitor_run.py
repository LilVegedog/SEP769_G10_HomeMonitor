import os, time, subprocess, threading
import RPi.GPIO as GPIO

# ==== 引脚定义（BCM）====
SND_PIN  = 25   # LM393 D0
LED_PIN  = 22   # 主动高
BUZZ_PIN = 23   # 有源蜂鸣器，低电平触发
SERVO    = 12   # 仅底部舵机信号线（你当前接的是 BCM12）

# ==== 动作参数 ====
ANGLES = [20, 60, 100, 140]   # 依据你的云台安全角度调整
PHOTO_DIR = "captures"
RES_W, RES_H = 2592, 1944     # OV5647 原生分辨率
ROTATE = "180"                # 需要就用 "180"，不需要就用 "0"
MOVE_SETTLE = 0.6             # 舵机转动后的稳定时间
ALARM_SEC = 3.0               # 报警声+LED闪烁持续秒数
COOLDOWN  = 2.0               # 一次动作完成后的冷却期
DEBOUNCE_MS = 20              # 去抖

# ==== 初始化 ====
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN,  GPIO.OUT); GPIO.output(LED_PIN, 0)
GPIO.setup(BUZZ_PIN, GPIO.OUT); GPIO.output(BUZZ_PIN, 0)  # 低电平响，所以先拉高=静音
GPIO.setup(SND_PIN,  GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(SERVO, GPIO.OUT)
pwm = GPIO.PWM(SERVO, 50)   # SG90: 50Hz, 20ms周期
pwm.start(0)

def set_angle(angle):
    angle = max(0, min(180, angle))
    duty = 2 + angle/18.0   # 0°≈2%, 180°≈12%
    GPIO.output(LED_PIN, GPIO.input(LED_PIN))  # 占位，避免linter警告
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.35)
    pwm.ChangeDutyCycle(0)

def shoot(angle):
    ts = time.strftime("%Y%m%d_%H%M%S")
    os.makedirs(PHOTO_DIR, exist_ok=True)
    fname = f"{PHOTO_DIR}/{ts}_a{angle}.jpg"
    cmd = [
        "rpicam-still",
        "-n",
        "-o", fname,
        "--timeout", "500",
        "--width", str(RES_W),
        "--height", str(RES_H),
        "--rotation", ROTATE,
    ]
    subprocess.run(cmd, check=True)
    print("saved:", fname)

def blink_and_buzz(duration=ALARM_SEC, blink_hz=6):
    """在后台线程里蜂鸣+闪灯，不阻塞主线程扫角度拍照。"""
    period = 1.0 / blink_hz
    end = time.monotonic() + duration
    try:
        while time.monotonic() < end:
            # 蜂鸣器响 + LED亮
            GPIO.output(BUZZ_PIN, 1)   
            GPIO.output(LED_PIN, 1)
            time.sleep(period/2)
            # 蜂鸣器停 + LED灭
            GPIO.output(BUZZ_PIN, 0)
            GPIO.output(LED_PIN, 0)
            time.sleep(period/2)
    finally:
        GPIO.output(BUZZ_PIN, 1)
        GPIO.output(LED_PIN, 0)

def sweep_and_shoot():
    # 先回中位（可按你需要注释/保留）
    set_angle(90); time.sleep(0.5)
    for a in ANGLES:
        print("→ move to", a)
        set_angle(a)
        time.sleep(MOVE_SETTLE)
        shoot(a)
    # 收尾回中
    set_angle(90)

armed_until = 0.0

def on_edge(_):
    global armed_until
    now = time.monotonic()
    # 冷却期内忽略
    if now < armed_until:
        return
    # 多数LM393是触发=LOW；若你的模块相反，可改为检测RISING或直接删判断
    if GPIO.input(SND_PIN) == 0:
        print(time.strftime("%H:%M:%S"), "Sound DETECTED")
        armed_until = now + COOLDOWN  # 先占位，避免并发多次进来

        # 后台闪灯+蜂鸣
        th = threading.Thread(target=blink_and_buzz, args=(ALARM_SEC,), daemon=True)
        th.start()

        # 主线程扫角度并拍照
        try:
            sweep_and_shoot()
        except Exception as e:
            print("capture error:", e)

        # 冷却期从此刻重新计
        armed_until = time.monotonic() + COOLDOWN
        print("cycle done, cooling down...")

try:
    # 同时监听上升/下降沿，更稳健；由回调内判断电平
    GPIO.add_event_detect(SND_PIN, GPIO.BOTH, callback=on_edge, bouncetime=DEBOUNCE_MS)
    print("Ready. Clap or make a sharp sound to trigger.  Ctrl+C to exit.")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    GPIO.output(LED_PIN, 0)
    GPIO.output(BUZZ_PIN, 1)
    pwm.stop()
    GPIO.cleanup()
