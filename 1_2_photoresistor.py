from machine import ADC
from time import sleep

photoresistor = ADC(0)

while True:
    light = photoresistor.read()
    print("Light Level:", light)
    sleep(0.5)