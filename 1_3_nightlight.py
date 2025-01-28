from machine import ADC, Pin
from time import sleep

photoresistor = ADC(0)
led = Pin(2, Pin.OUT)
LIMIT = 300

while True:
    light = photoresistor.read()
    
    if light  < LIMIT:
        led.on()
    else:
        led.off()
    
    print("Light Level:", light)
    sleep(0.2)