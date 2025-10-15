import RPi.GPIO as GPIO
import time

SND = 25
GPIO.setmode(GPIO.BCM)
GPIO.setup(SND, GPIO.IN, pull_up_down=GPIO.PUD_UP)
print("Detecting sound...ctrl+c to stop:")
try:
	while True:
		state = GPIO.input(SND)
		if state == 0:
			print("Detected!")
		else:
			print("quiet...")
		time.sleep(0.05)
except KeyboardInterrupt:
	print("\nTest Stopped.")
finally:
	GPIO.cleanup()
