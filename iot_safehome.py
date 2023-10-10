import RPi.GPIO as GPIO
import time
from time import sleep

attending = True
risk = False
hazard = False
counter = 0
base_temp = 0
GPIO.setmode(GPIO.BOARD)       # use PHYSICAL GPIO Numbering

DHTPin_1, DHTPin_2  = 11, 13
dht1 = DHT.DHT(DHTPin_1)   #create a DHT class object
dht2 = DHT.DHT(DHTPin_2)   #create a DHT class object
GPIO.setup(36, GPIO.OUT)   # set the ledPin to OUTPUT mode
GPIO.output(36, GPIO.LOW) 
GPIO.setup(32, GPIO.OUT)   # set the buzzerPin to OUTPUT mode
GPIO.output(32, GPIO.LOW)
GPIO.setup(15,GPIO.IN)

def calculate_temperature(sensor1, sensor2):
    chk1 = sensor1.readDHT11()     #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
    chk2 = sensor2.readDHT11()
    if (chk1 is dht1.DHTLIB_OK and chk2 is dht2.DHTLIB_OK):      #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
        return (sensor1.temperature + sensor2.temperature)/2
    else:
        return -999.999

def calculate_humidity(sensor1, sensor2):
    chk1 = sensor1.readDHT11()     #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
    chk2 = sensor2.readDHT11()
    if (chk1 is dht1.DHTLIB_OK and chk2 is dht2.DHTLIB_OK):      #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
        return (sensor1.humidity + sensor2.humidity)/2
    else:
        return -999.999

def check_risk(base_temp, current_temp, humidity, smoke):
    if (current_temp - base_temp >= 12.0):
        if humidity < 0.15:
            risk = True
        elif smoke == True:
            risk = True

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
