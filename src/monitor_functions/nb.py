import RPi.GPIO as GPIO
import time

BUZZER_PIN = 23
FREQ = 2500       

def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUZZER_PIN, GPIO.OUT)

    pwm = GPIO.PWM(BUZZER_PIN, FREQ)

    try:
        print("Buzzer test started, press Ctrl+C to stop.")

        while True:
            pwm.start(50)      
            time.sleep(0.5)    
            pwm.stop()
            time.sleep(0.5)    
    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        pwm.stop()
        GPIO.cleanup()

if __name__ == "__main__":
    main()
