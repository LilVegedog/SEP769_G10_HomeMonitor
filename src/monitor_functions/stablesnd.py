import RPi.GPIO as GPIO, time

SND = 25
TRIGGER_ON_LOW = True
DEBOUNCE = 10
QUIET_ARM_MS = 50

GPIO.setmode(GPIO.BCM)
GPIO.setup(SND, GPIO.IN, pull_up_down=GPIO.PUD_UP)
ACTIVE = 0 if TRIGGER_ON_LOW else 1
INACT = 1 - ACTIVE
INACT = 1 - ACTIVE

last_state = GPIO.input(SND)
last_change = time.monotonic()
armed = True

def now_s():
	return f"{time.time():.3f}"
	
print("Listening...ctrl+c to exit...")
try:
	GPIO.add_event_detect(SND, GPIO.BOTH, bouncetime=DEBOUNCE)
	while True:
		if GPIO.event_detected(SND):
			s = GPIO.input(SND)
			t = time.monotonic()
			if s != last_state:
				last_state = s
				last_change = t
			if armed and s == ACTIVE:
				print(f"{now_s()} Detected (level={s})")
				armed = False
			if (s == INACT) and ((t - last_change) * 1000 >= QUIET_ARM_MS):
				if not armed:
					print(f"{now_s()} re-armed")
				armed = True
		time.sleep(0.002)
except KeyboardInterrupt:
	pass
finally:
	GPIO.cleanup()
