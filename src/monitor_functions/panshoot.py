import os, time, subprocess
import RPi.GPIO as GPIO

SERVO = 12
ANGLES = [20, 60, 100, 140]
DELAY_AFT_MV = 0.7
OUTDIR = "captures"
RES_W, RES_H = 2592, 1944

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO, GPIO.OUT)
pwm = GPIO.PWM(SERVO, 50)
pwm.start(0)

def set_angle(angle):
	duty = 2 + angle / 18.0
	pwm.ChangeDutyCycle(duty)
	time.sleep(0.35)
	pwm.ChangeDutyCycle(0)
	
def shoot(angle):
	ts = time.strftime("%Y%m%d_%H%M%S")
	os.makedirs(OUTDIR, exist_ok=True)
	fname = f"{OUTDIR}/{ts}_a{angle}.jpg"
	cmd = [
		"rpicam-still",
		"-n",
		"-o", fname,
		"--timeout", "500"
		"--width", str(RES_W),
		"--height", str(RES_H),
		"--rotation", "180",
	]
	subprocess.run(cmd, check=True)
	print("saved: ", fname)

try:
	
	# set_angle(90)
	time.sleep(0.5)
	for a in ANGLES:
		print("--> move to", a)
		set_angle(a)
		time.sleep(DELAY_AFT_MV)
		shoot(a)
		
		time.sleep(DELAY_AFT_MV)
	set_angle(90)
	
	print("Done!")
except KeyboardInterrupt:
	pass
finally:
	pwm.stop()
	GPIO.cleanup()
