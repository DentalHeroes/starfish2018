#  ****************************************************************************
#  * To create a buzzing sounds using a passive piezo buzzer and DC current,  *
#  * a square wave must be sent to the piezo. This can be accomplished by     *
#  * rapidly sending high and low pulses to the piezo buzzer.                 *
#  ****************************************************************************

import RPi.GPIO as GPIO
import time
   
#LED connected to board pin 11
LEDPIN = 11

#Buzzer connected to board pin 16
BUZZPIN = 16

def setup():
    # Set the GPIO modes to board Numbering
    GPIO.setmode(GPIO.BOARD)
	#set LEDPIN's mode to output,and initial level to LOW(0V)
    GPIO.setup(LEDPIN,GPIO.OUT,initial=GPIO.LOW)	
    # Set BUZZPIN's mode to output, 
    # and initial level to High(5.0v)
    GPIO.setup(BUZZPIN, GPIO.OUT, initial=GPIO.HIGH)

"""
Sends an alert by blinking the LED light
and sending a square wave to the buzzer

Args:
	repeat: number of times to repeat the alert

"""	
def alert(repeat):
	#loop through and beep, {repeat} times
	for i in range(0, repeat):
		#turn LED on
		GPIO.output(LEDPIN,GPIO.HIGH)
		#square wave loop
		for pulse in range(60):
			#set buzzer low
			GPIO.output(BUZZPIN, GPIO.LOW)
			time.sleep(0.0009)
			#set buzzer high
			GPIO.output(BUZZPIN, GPIO.HIGH)
			time.sleep(0.0009)
		#turn LED off
		GPIO.output(LEDPIN,GPIO.LOW)
		#rest between beeps
		time.sleep(0.3)
		

def destroy():
	# Turn off buzzer and LED light
	GPIO.output(BUZZPIN, GPIO.LOW)
	GPIO.output(LEDPIN,GPIO.LOW)
	# Release resource
	GPIO.cleanup()
	
def sendAlert():
	#set the GPIO mode and initial ouputs
	setup()
	#send alerts
	alert(6)
	#turn off outputs and releast resources
	destroy()
