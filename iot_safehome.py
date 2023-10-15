import RPi.GPIO as GPIO
import time
import sys
from time import sleep
import Freenove_DHT as DHT
import requests
from datetime import datetime
import urllib.parse
from pymongo import MongoClient

dht11_pin1, dht11_pin2 = 11, 13
button_pin = 22
mq2_pin = 15
led_pin = 36
buzzer_pin = 32
flame_pin = 16
led_gas_pin = 31
mq5_pin = 29
db_ip = sys.argv[1]
postal = sys.argv[2]

def get_db_client_connection():
    global dp_ip
    host = sys.argv[1]
    port = 27017
    user_name = "db_admin"
    pass_word = "admin"  
    db_name = "admin"  # database name to authenticate
    # if your password has '@' then you might need to escape hence we are using "urllib.parse.quote_plus()" 
    client = MongoClient(f'mongodb://{user_name}:{urllib.parse.quote_plus(pass_word)}@{host}:{port}/{db_name}') 
    return client

def db_insert(mydict):
    myclient = get_db_client_connection()
    mydb = myclient["iot_db"]
    mycol = mydb["safehome_iot_records"]
    mycol.insert_one(mydict)

def calculate_temperature(sensor1, sensor2):
    sensor1.readDHT11()
    sensor2.readDHT11()
    return (sensor1.temperature + sensor2.temperature)/2
    
def calculate_humidity(sensor1, sensor2):
    sensor1.readDHT11()
    sensor2.readDHT11()
    return (sensor1.humidity + sensor2.humidity)/2
    
def check_risk(base_temp, current_temp, humidity, smoke):
    if (current_temp - base_temp >= 12.0):
        if humidity < 25.0:
            return True
        elif check_smoke_and_gas(mq2_pin):
            return True
        else:
            return False
    else:
        return False

def check_smoke_and_gas(mq2):
    if GPIO.input(mq2) != 1:
        return True
    else:
        return False
        
def check_flame(flame):
    if GPIO.input(flame) == 1:
        return True
    else:
        return False
        
def check_gas_leak(gas):
    if GPIO.input(gas) != 1:
        return True
    else:
        return False

def set_gas_alert(led_gas_pin, buzzer_pin):
    print("ALERT: GAS LEAKING!")
    GPIO.output(led_gas_pin, GPIO.HIGH)
    GPIO.output(buzzer_pin, GPIO.HIGH)
    
def set_warning(led_pin):
    GPIO.output(led_pin, GPIO.HIGH)
    print("WARNING: RISK OF FIRE")

def check_hazard(hazard_flag, counter):
    if (hazard_flag == True and counter > 30):
        return  True
    else:
        return False

def set_alarm(led_pin, buzzer_pin):
    GPIO.output(led_pin, GPIO.HIGH)
    GPIO.output(buzzer_pin, GPIO.HIGH)
    print("ALERT: HAZARD OF FIRE")
    
def reset_alert_sent(clock):
    if (clock > 10) and (clock % 100 == 0):
        return False
    else:
        return True

def reset_actuators():
    GPIO.output(led_pin, GPIO.LOW)
    GPIO.output(buzzer_pin, GPIO.LOW)
    GPIO.output(led_gas_pin, GPIO.LOW)
    
def button_pressed(button_pin):
    if GPIO.input(button_pin)==GPIO.LOW: # if button is pressed
        return True

def send_alert_message(code):
    now = datetime.now()
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    msg_1 = "ALERT: HAZARD OF FIRE."
    msg_2 = "ALERT: HAZARD OF GAS LEAKING."
    message = [msg_1, msg_2]
    TOKEN = "6467940306:AAEjeCNWQcU3qQYl2f7Ck5Tv9lTBHIvejes"
    chat_id = "5260152724"
    message = "{} - {}".format(dt_string, message[code-1])
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
    requests.get(url).json() # this sends the message
    
def execute(sensor1, sensor2):
    clock = 0
    risk = False
    hazard = False
    warning_flag = False
    smoke = False
    gas_leak = False
    gas_msg_sent = False
    fire_msg_sent = False
    counter = 0
    base = base_temp
    
    while True:
        record = {}
        record["risk"] = False
        record["hazard"] = False
        now = datetime.now()
        # dd/mm/YY H:M:S
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        record["datetime"] = dt_string
        clock += 1
        current_temp = calculate_temperature(sensor1, sensor2)
        print("current average temperature: %5.2f" % (current_temp))
        current_humid = calculate_humidity(sensor1, sensor2)
        print("current average humidity: %5.2f" % (current_humid))
        record["base temperature"] = base
        record["current_temperature"] = current_temp
        record["current_humidity"] = current_humid
                                
        if current_temp != -999.999 and current_humid != -999.999:
            risk = check_risk(base, current_temp, current_humid, check_smoke_and_gas(mq2_pin))
            smoke = check_smoke_and_gas(mq2_pin)
            check_hazard(risk, counter)
            sleep(3)
        else:
            print("DHT11 sensors get errors!")
            break
            
        if risk == True:
            warning_flag = True
            set_warning(led_pin)
        
        if check_gas_leak(mq5_pin):
            gas_leak = True
            
        record["gas_alert_on"] = False
        if gas_leak:
            set_gas_alert(led_gas_pin, buzzer_pin)
            record["gas_alert_on"] = True            
            if gas_msg_sent == False:
                send_alert_message(2)
                gas_msg_sent = True            
        
        if warning_flag == True:
            counter += 1
            hazard = check_hazard(warning_flag, counter)
            print("counter: %d" % (counter))
        record["fire_alert_on"] = False
        flame = check_flame(flame_pin)
        record["flame_deteced"] = flame
        if (hazard == True) or (flame):
            set_alarm(led_pin, buzzer_pin)
            record["fire_alert_on"] = True
            record["flame_deteced"] = flame
            risk = True
            warning_flag = True
            hazard = True
            if fire_msg_sent == False:
                send_alert_message(1)
                fire_msg_sent = True
        record["risk"] = risk
        record["warning_flag"] = warning_flag
        record["smoke_detected"] = smoke
        record["gas_leak"] = gas_leak
        record["hazard"] = hazard
        record["fire_msg_sent"] = fire_msg_sent
        record["gas_msg_sent"] = gas_msg_sent
        
        record["postal"] = sys.argv[2]
        
        if button_pressed(button_pin):
            record["button_pressed"] = True
            risk = False
            warning_flag = False
            hazard = False
            gas_leak = False
            smoke = False
            flame = False
            gas_msg_sent = False
            fire_msg_sent = False            
            
            try:
                db_insert(record)
            except:
                print("Database insertion failed.")
            counter = 0
            reset_actuators()
            print("reset button pressed!")
            base = (base + calculate_temperature(sensor1, sensor2))/2
            print("new base temperature: %5.2f" % (base))
        else:
            record["button_pressed"] = False
        
        if(clock % 20 == 0):
            try:
                db_insert(record)
            except:
                print("Database insertion failed.")
        if(fire_msg_sent):
            fire_msg_sent = reset_alert_sent(clock)
        if(gas_msg_sent):
            gas_msg_sent = reset_alert_sent(clock)
        print(fire_msg_sent)
        print(gas_msg_sent)
        clock %= 101

        

if __name__ == "__main__":          
    GPIO.setmode(GPIO.BOARD)       # use PHYSICAL GPIO Numbering
    DHTPin_1, DHTPin_2  = 11, 13
    button_pin = 22
    dht1 = DHT.DHT(dht11_pin1)   #create a DHT class object
    dht2 = DHT.DHT(dht11_pin2)   #create a DHT class object
    GPIO.setup(36, GPIO.OUT)   # set the ledPin to OUTPUT mode
    GPIO.output(36, GPIO.LOW) 
    GPIO.setup(32, GPIO.OUT)   # set the buzzerPin to OUTPUT mode
    GPIO.output(32, GPIO.LOW)
    GPIO.setup(15,GPIO.IN)
    GPIO.setup(16,GPIO.IN)
    GPIO.setup(29,GPIO.IN)
    GPIO.setup(31,GPIO.OUT)
    GPIO.output(31, GPIO.LOW)
    GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # set buttonPin to PULL UP INPUT mode
    chk1 = dht1.readDHT11()     #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
    chk2 = dht2.readDHT11()
    try:
        if chk1 is dht1.DHTLIB_OK and chk2 is dht2.DHTLIB_OK:
            print("sensors are setup correctly!")    
            base_temp = calculate_temperature( dht1,  dht2)
            print("starting average base temperature of the area: %5.2f" % (base_temp))
            execute(dht1, dht2)
        else:
            print("Sensors are not setup correctly!")
    finally:
        print("cleaning up.")
        GPIO.cleanup()
