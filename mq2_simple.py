import RPi.GPIO as GPIO

import time
from time import sleep

GPIO.setmode(GPIO.BOARD)       # use PHYSICAL GPIO Numbering
GPIO.setup(36, GPIO.OUT)   # set the ledPin to OUTPUT mode
GPIO.output(36, GPIO.LOW) 
GPIO.setup(32, GPIO.OUT)   # set the buzzerPin to OUTPUT mode
GPIO.output(32, GPIO.LOW)

GPIO.setup(15,GPIO.IN)

try:
    while True:
        if GPIO.input(15) != 1:
            print(" WARNING: gas detected.")
            GPIO.output(36, GPIO.HIGH)
            GPIO.output(32, GPIO.HIGH)
            sleep(3)
        else:
            GPIO.output(36, GPIO.LOW)
            GPIO.output(32, GPIO.LOW)
            print("normal.")
            sleep(3)
finally:
    print("cleaning up.")
    GPIO.cleanup()
