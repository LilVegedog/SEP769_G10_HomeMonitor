import RPi.GPIO as GPIO
from time import sleep


GPIO.setmode(GPIO.BCM)
LED_PIN = 22
GPIO.setup(LED_PIN, GPIO.OUT)

print("Testing LED")
for i in range(5):
	GPIO.output(LED_PIN, GPIO.HIGH)
	print("On")
	sleep(0.5)
	GPIO.output(LED_PIN, GPIO.LOW)
	print("Off")
	sleep(0.5)
	
GPIO.cleanup()
print("Yah")
