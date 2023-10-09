#!/usr/bin/env python3
#############################################################################
# Filename    : DHT11.py
# Description :	read the temperature and humidity data of DHT11
# Author      : freenove
# modification: 2020/10/16
########################################################################
import RPi.GPIO as GPIO
import time
import Freenove_DHT as DHT
DHTPin_1, DHTPin_2  = 11, 13     #define the pin of DHT11

def loop():
    dht1 = DHT.DHT(DHTPin_1)   #create a DHT class object
    dht2 = DHT.DHT(DHTPin_2)   #create a DHT class object
    counts = 0 # Measurement counts
    while(True):
        counts += 1
        print("Measurement counts: ", counts)
        for i in range(0,15):            
            chk1 = dht1.readDHT11()     #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
            chk2 = dht2.readDHT11()
            if (chk1 is dht1.DHTLIB_OK):      #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
                print("DHT11_1,OK!")
                break
            if (chk2 is dht2.DHTLIB_OK):      #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
                print("DHT11_2,OK!")
                break
            time.sleep(0.1)
        print("Sensor 1: Humidity : %.2f, \t Temperature : %.2f \n"%(dht1.humidity,dht1.temperature))
        print("Sensor 2: Humidity : %.2f, \t Temperature : %.2f \n"%(dht2.humidity,dht2.temperature))
        time.sleep(2)       
        
if __name__ == '__main__':
    print ('Program is starting ... ')
    try:
        loop()
    except KeyboardInterrupt:
        GPIO.cleanup()
        exit()  

