import RPi.GPIO as GPIO
import time
from time import sleep
import Freenove_DHT as DHT

dht11_pin1, dht11_pin2 = 11, 13
button_pin = 12
mq2_pin = 15
led_pin = 36
buzzer_pin = 32


def calculate_temperature(sensor1, sensor2):
    sensor1.readDHT11()
    sensor2.readDHT11()
    return (sensor1.temperature + sensor2.temperature)/2
    
def calculate_humidity(sensor1, sensor2):
    sensor1.readDHT11()
    sensor2.readDHT11()
    return (sensor1.humidity + sensor2.humidity)/2
    
def check_risk(base_temp, current_temp, humidity, smoke):
    if (current_temp - base_temp >= 1.0):
        if humidity < 25.0:
            return True
        elif check_smoke_and_gas(mq2_pin):
            return True
        else:
            return False

def check_smoke_and_gas(mq2):
    if GPIO.input(mq2) != 1:
        return True
    else:
        return False

def set_warning(led_pin):
    GPIO.output(led_pin, GPIO.HIGH)
    print("WARNING: RISK OF FIRE")

def check_hazard(risk, counter):
    if (risk == True and counter > 10):
        return  True

def set_alarm(led_pin, buzzer_pin):
    GPIO.output(led_pin, GPIO.HIGH)
    GPIO.output(buzzer_pin, GPIO.HIGH)
    print("WARNING: HAZARD OF FIRE")

def reset_actuators():
    GPIO.output(led_pin, GPIO.LOW)
    GPIO.output(buzzer_pin, GPIO.LOW)
    
def execute(sensor1, sensor2):
    risk, hazard = False, False
    warning_flag = False
    counter = 0
    base = base_temp
    while True:
        current_temp = calculate_temperature(sensor1, sensor2)
        print(current_temp)
        current_humid = calculate_humidity(sensor1, sensor2)
        print(current_humid)
        if current_temp != -999.999 and current_humid != -999.999:
            risk = check_risk(base, current_temp, current_humid, check_smoke_and_gas(mq2_pin))
            check_hazard(risk, counter)
        else:
            print("DHT11 sensors get errors!")
            break
        if risk == True:
            warning_flag = True
        if warning_flag == True:
            set_warning(led_pin)
            counter += 1
            hazard = check_hazard(risk, counter)
            print("counter: %d" % (counter))

        if hazard == True:
            set_alarm(led_pin, buzzer_pin)

        if GPIO.input(button_pin)==GPIO.LOW: # if button is pressed
            risk = False
            warning_flag = False
            hazard = False
            counter = 0
            reset_actuators()
            print("reset button pressed!")
            base = (base + calculate_temperature(sensor1, sensor2))/2
            print("new base temperature: %5.2f" % (base))
        sleep(3)

if __name__ == "__main__":          
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
    chk1 = dht1.readDHT11()     #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
    chk2 = dht2.readDHT11()
    try:
        if chk1 is dht1.DHTLIB_OK and chk2 is dht2.DHTLIB_OK:
            print("sensors are setup correctly!")    
            base_temp = calculate_temperature( dht1,  dht2)
            print("starting base temperature: %5.2f" % (base_temp))
            execute(dht1, dht2)
        else:
            print("Sensors are not setup correctly!")
    finally:
        print("cleaning up.")
        GPIO.cleanup()
