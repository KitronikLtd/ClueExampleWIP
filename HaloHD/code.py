import math
import board
import digitalio
import time
import neopixel
import busio
from adafruit_clue import clue
from Kitronik_MCP7940_RTC import KitronikRTC


#a common interface for the setting of a time value using the ZIP LEDs as user feedback
def timeSetInterface():
    setHrs = 0
    setMns = 0
    AM = True
    DisplayAMPM = False
    #'Zero' the clock display so we can set it
    zip_halo_display.fill(0)
    zip_halo_display[5*setHrs] = (255,0,0)
    zip_halo_display.show()
    #because the ui is limited we will have to set the hours and mins seperately.
    #Pressing A increments the value, B enters it and moves on
    # set the time in Hours, Minutes, and then AM/PM
    print("A to Adjust, B to Enter")
    #pressed = clue.were_pressed
    print("Hours")
    #while (not (clue.were_pressed == {'B'})):
    while (not (clue.button_b)):
        if (clue.button_a) :
            setHrs += 1
            if(setHrs >11):
                setHrs =0
            zip_halo_display.fill(0)
            zip_halo_display[5*setHrs] = (255,0,0)
            zip_halo_display.show()
        time.sleep(0.1) #add a little debounce
    print("Minutes")
    time.sleep(0.5) #add a little debounce
    #while (not (clue.were_pressed == {'B'})):
    while (not (clue.button_b)):
        if (clue.button_a) :
            setMns += 1
            if(setMns >59):
                setMns = 0
            zip_halo_display.fill(0)
            zip_halo_display[5*setHrs] = (255,0,0)
            zip_halo_display[setMns] = (0,255,0)
            zip_halo_display.show()
        time.sleep(0.1) #debounce
    print("AM")
    time.sleep(0.5)
    while (not (clue.button_b)):
        if clue.button_a:
            if(AM):
                AM = False
            else:
                AM = True
            DisplayAMPM = True
        if(DisplayAMPM):
            if(AM ==True):
                print("AM")
            else:
                print("PM")
            DisplayAMPM = False
        time.sleep(0.1)
    if(AM == False):
        setHrs += 12
    time.sleep(0.5)
    print(setHrs,":",setMns)
    return (setHrs,setMns)

# a procedure to allow the user to set the time
def userSetTime():
    print("Setting Time")
    requestedTime = timeSetInterface()
    #done hours, done mins, poke the rtc with the new values.
    rtc.setTime(requestedTime[0], requestedTime[1], 0)
    time.sleep(0.5) #pause to allow user to have released the buttons.

# a procedure to allow the user to set an alarm
def userSetAlarm():
    print("Setting Alarm")
    global alarmHour
    global alarmMinute
    global setAlarm
    requestedTime = timeSetInterface()
    alarmHour = requestedTime[0]
    alarmMinute = requestedTime[1]
    print("A") #indicate to the user there is an alarm set
    setAlarm = True
    time.sleep(0.1) #pause to allow user to have released the buttons.
    #done - The main loop checks the time to see if we should alarm


# Declare constants
LEDS_ON_HALO = 60
i2c = clue._i2c
rtc = KitronikRTC()
zipHours = 0
setAlarm = False
alarmHour = 0
alarmMinute = 0

zip_halo_display = neopixel.NeoPixel(board.P8, LEDS_ON_HALO)

while True:
    pressed = clue.were_pressed
    if (pressed == {'A'}) :
        userSetTime()
    elif(pressed == {'B'}) :
        userSetAlarm()
    else:
        rtc.readValue()
        hours = rtc.readHrs()

        minutes = rtc.readMin()
        seconds = rtc.readSec()
        if hours > 13:
            zipHours = hours - 12
        else:
            zipHours = hours
        zipHours = zipHours * 5
        zip_halo_display.fill(0)
        zip_halo_display[zipHours] = (255, 0, 0)
        zip_halo_display[minutes] = (0, 255, 0)
        zip_halo_display[seconds] = (0, 0, 255)
        print("Time:",zipHours,":",minutes,":",seconds,"  24hr",hours)
        zip_halo_display.show()
        if setAlarm == True:
            if alarmHour == hours:
                if alarmMinute == minutes:
                    soundlevel = 0
                    while soundlevel < (SOUND_LEVEL_BASE + 5):
                        soundlevel = pin0.read_analog()
                        play(BA_DING, pin14, True, False)
                    setAlarm = False
                    stop(pin14) #the music
        time.sleep(0.99) #this sleep reduces the flicker on the updating of the display every time round the loop.
