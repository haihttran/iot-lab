import RPi.GPIO as GPIO
import time
from time import sleep
import Freenove_DHT as DHT

dht11_pin1, dht11_pin2 = 11, 13
button_pin = 12
mq2_pin = 15
led_pin = 36
buzzer_pin = 32

attending = True
risk = False
hazard = False
counter = 0
base_temp = 0

def calculate_temperature(sensor1, sensor2):
    chk1 = sensor1.readDHT11()     #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
    chk2 = sensor2.readDHT11()
    if (chk1 is sensor1.DHTLIB_OK and chk2 is sensor2.DHTLIB_OK):      #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
        return (sensor1.temperature + sensor2.temperature)/2
    else:
        return -999.999

def calculate_humidity(sensor1, sensor2):
    chk1 = sensor1.readDHT11()     #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
    chk2 = sensor2.readDHT11()
    if (chk1 is sensor1.DHTLIB_OK and chk2 is sensor2.DHTLIB_OK):      #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
        return (sensor1.humidity + sensor2.humidity)/2
    else:
        return -999.999

def check_risk(base_temp, current_temp, humidity, smoke):
    if (current_temp - base_temp >= 1.0):
        if humidity < 0.15:
            risk = True
        elif check_smoke_and_gas(mq2_pin):
            risk = True
        else:
            risk = False

def check_smoke_and_gas(mq2):
    if GPIO.input(mq2) != 1:
        return True
    else:
        return False

def set_warning(led_pin):
    if risk == True:        
        GPIO.output(led_pin, GPIO.HIGH)
        print("WARNING: RISK OF FIRE")
        sleep(3)
    else:
        GPIO.output(led_pin, GPIO.LOW)
        print("NORMAL.")
        sleep(3)

def check_hazard():
    if (counter > 9000):
        hazard =  True

def set_alarm(led_pin, buzzer_pin):
    if hazard == True:        
        GPIO.output(led_pin, GPIO.HIGH)
        GPIO.output(buzzer_pin, GPIO.HIGH)
        print("WARNING: RISK OF FIRE")
        sleep(3)
    else:
        GPIO.output(led_pin, GPIO.LOW)
        GPIO.output(buzzer_pin, GPIO.LOW)
        print("NORMAL.")
        sleep(3)

def execute(sensor1, sensor2):
    while True:
        current_temp = calculate_temperature(sensor1, sensor2)
        current_humid = calculate_humidity(sensor1, sensor2)
        if current_temp != -999.999 and current_humid != -999.999:
            check_risk(base_temp, current_temp, current_humid, check_smoke_and_gas(mq2_pin, led_pin, buzzer_pin))
        else:
            print("DHT11 sensors get errors!")
            break

        if risk == True:
            set_warning(led_pin)

        if hazard == True:
            set_alarm(led_pin, buzzer_pin)

        if GPIO.input(button_pin)==GPIO.LOW: # if button is pressed
            risk = False
            hazard = False

def main():           
    GPIO.setmode(GPIO.BOARD)       # use PHYSICAL GPIO Numbering
    DHTPin_1, DHTPin_2  = 11, 13
    button_pin = 12
    dht1 = DHT.DHT(dht11_pin1)   #create a DHT class object
    dht2 = DHT.DHT(dht11_pin2)   #create a DHT class object
    GPIO.setup(36, GPIO.OUT)   # set the ledPin to OUTPUT mode
    GPIO.output(36, GPIO.LOW) 
    GPIO.setup(32, GPIO.OUT)   # set the buzzerPin to OUTPUT mode
    GPIO.output(32, GPIO.LOW)
    GPIO.setup(15,GPIO.IN)
    GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # set buttonPin to PULL UP INPUT mode
    base_temp = calculate_temperature( dht1,  dht2)
    try:
        execute(dht1, dht2)
    finally:
        print("cleaning up.")
        GPIO.cleanup()
