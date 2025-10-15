import RPi.GPIO as GPIO
import time

SOUND_PIN = 25

GPIO.setmode(GPIO.BCM)
GPIO.setup(SOUND_PIN, GPIO.IN)

print("detecting sound")
try:
    while True:
        if GPIO.input(SOUND_PIN) == GPIO.LOW:
            print("detected!")
        time.sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()
