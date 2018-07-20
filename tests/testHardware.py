#!/usr/bin/python

import RPi.GPIO as GPIO
import time

BUZZPIN = 16
LEDPIN = 11
SENSORPIN = 8

def print_message():
    print ('|*****************************|')
    print ('|        Test Hardware        |')
    print ('|  -------------------------  |')
    print ('|      BUZZER will beep       |')
    print ('|       LED will blink        |')
    print ('|  SENSOR will show raw data  |')
    print ('|*****************************|\n')
    print ('Program is running...')
    print ('Please press Ctrl+C to end the program...')

def beep(repeat):
	for i in range(0, repeat):
		for pulse in range(60):
			GPIO.output(BUZZPIN, GPIO.LOW)
			time.sleep(0.0005)
			GPIO.output(BUZZPIN, GPIO.HIGH)
			time.sleep(0.0005)
		time.sleep(0.02)

def getData():
    GPIO.setup(SENSORPIN, GPIO.OUT)
    GPIO.output(SENSORPIN, GPIO.HIGH)
    time.sleep(0.05)

    GPIO.output(SENSORPIN, GPIO.LOW)
    time.sleep(0.02)

    GPIO.setup(SENSORPIN, GPIO.IN, GPIO.PUD_UP)
    MAX_UNCHANGE_COUNT = 100
    unchanged_count = 0
    last = -1
    data = []
    while True:
        current = GPIO.input(SENSORPIN)
        data.append(current)
        if last != current:
            unchanged_count = 0
            last = current
        else:
            unchanged_count += 1
            if unchanged_count > MAX_UNCHANGE_COUNT:
                break
    print data

def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(BUZZPIN, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(LEDPIN, GPIO.OUT, initial=GPIO.LOW)

def destroy():
    GPIO.output(LEDPIN, GPIO.LOW)
    GPIO.cleanup()

def main():
    print_message()
    while True:
       GPIO.output(LEDPIN, GPIO.HIGH)
       beep(2)
       getData()
       time.sleep(1)
       
       GPIO.output(LEDPIN, GPIO.LOW)
       time.sleep(1.0)

if __name__ == '__main__':
    setup()
    try:
        main()
    except KeyboardInterrupt:
        destroy()
