# A 'free roaming' robot example for Adafruit CLUE on Kitronik :MOVE motor buggy chassis.
# Uses the ultrasonic to detect an obstacle and indicates a range using the LEDs
# If something is close and in the way then stop, beep the horn and turn away

import board
import digitalio
import pulseio
import time
import neopixel
import busio
import adafruit_hcsr04
import math
import MOVEmotor

sonar = adafruit_hcsr04.HCSR04(trigger_pin=board.P13, echo_pin=board.P14)
pixels  = neopixel.NeoPixel(board.P8,4)

#define some colours to make life easier
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)

#wrapper for the sonar to have try in. On error we will report a very short distance
def GetDistance():
    try:
        value = sonar.distance
    except RuntimeError:
        value =  1.0
    return value

def BeepHorn():
    #a beep beep
    buzzer = pulseio.PWMOut(board.P0,duty_cycle=2 ** 15, frequency=500, variable_frequency=True)
    time.sleep(0.5)
    buzzer.deinit()
    time.sleep(0.1)
    buzzer = pulseio.PWMOut(board.P0,duty_cycle=2 ** 15, frequency=500, variable_frequency=True)
    time.sleep(0.5)
    buzzer.deinit()

#Program starts here, fist setup the motor driver
MOVEmotor.setupMotorDriver()
#now loop doingt hemain code.
while True:
    distanceToObject = GetDistance()
    print ("Distance",distanceToObject)
    if( distanceToObject > 100): #clear run - go for it
        pixels.fill(GREEN)
        pixels.show()
        MOVEmotor.LeftMotor(255)
        MOVEmotor.RightMotor(255)
    elif( distanceToObject > 50): #approaching something, slow down
        pixels.fill(CYAN)
        pixels.show()
        MOVEmotor.LeftMotor(100)
        MOVEmotor.RightMotor(100)
    elif( distanceToObject > 20): #try and turn away
        pixels.fill(YELLOW)
        pixels.show()
        MOVEmotor.LeftMotor(100)
        MOVEmotor.RightMotor(50)
    else: #something in the way, stop and beep the horn
        pixels.fill(RED)
        pixels.show()
        MOVEmotor.StopMotors()
        #beep the horn
        BeepHorn()
        #Now try a different direction
        MOVEmotor.LeftMotor(-75)
        MOVEmotor.RightMotor(-75)
        time.sleep(0.3)
        MOVEmotor.LeftMotor(75)
        time.sleep(0.5)
