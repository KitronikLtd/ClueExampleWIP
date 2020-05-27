import board
import digitalio
import busio
import pulseio
import time
#from adafruit_clue import clue
from audiocore import WaveFile
from audiopwmio import PWMAudioOut as AudioOut

i2c = busio.I2C(board.P19, board.P20)
CHIP_ADDRESS = 0x0D

class PianoKeys:
    KEY_K0 = 0x100
    KEY_K1 = 0x200
    KEY_K2 = 0x400
    KEY_K3 = 0x800
    KEY_K4 = 0x1000
    KEY_K5 = 0x2000
    KEY_K6 = 0x4000
    KEY_K7 = 0x8000
    KEY_K8 = 0x01
    KEY_K9 = 0x02
    KEY_K10 = 0x04
    KEY_K11 = 0x08
    KEY_K12 = 0x10
    KEY_K13 = 0x20
    KEY_K14 = 0x40
        
keySensitivity = 8
keyNoiseThreshold = 5
keyRegValue = 0x0000

audio = AudioOut(board.P0)
    
buff = bytearray(1)
buff2 = bytearray(2)
buff3 = bytearray(5)
pin1 = digitalio.DigitalInOut(board.P1)
pin1.pull = digitalio.Pull.UP
pin1.direction = digitalio.Direction.INPUT
# Startup procedure
# Test /change pin is low, then test basic communication
if (pin1.value==0):
    # Reads the chip ID, should be 0x11 (chip ID addr = 0)
    buff[0] = 0
    while not i2c.try_lock():
        pass
    i2c.writeto(CHIP_ADDRESS, buff)
    i2c.readfrom_into(CHIP_ADDRESS, buff)
    while buff[0] != 0x11:
        i2c.readfrom_into(CHIP_ADDRESS, buff)
    
    # Change sensitivity (burst length) of keys 0-14 to keySensitivity (default is 8)
    for sensitivityReg in range(54, 69, 1):
        buff2[0] = sensitivityReg
        buff2[1] = keySensitivity
        i2c.writeto(CHIP_ADDRESS, buff2)

    # Disable key 15 as it is not used
    buff2[0] = 69
    buff2[1] = 0
    i2c.writeto(CHIP_ADDRESS, buff2)

    # Set Burst Repetition to keyNoiseThreshold (default is 5)
    buff2[0] = 13
    buff2[1] = keyNoiseThreshold
    i2c.writeto(CHIP_ADDRESS, buff2)
    
    #Configure Adjacent Key Suppression (AKS) Groups
    #AKS Group 1: ALL KEYS
    for aksReg in range(22, 37, 1):
        buff2[0] = aksReg
        buff2[1] = 1
        i2c.writeto(CHIP_ADDRESS, buff2)

    # Send calibration command
    buff2[0] = 10
    buff2[1] = 1
    i2c.writeto(CHIP_ADDRESS, buff2)
    i2c.unlock()

while not i2c.try_lock():
    pass
# Read all change status address (General Status addr = 2)
buff[0] = 2
i2c.writeto(CHIP_ADDRESS, buff)
i2c.readfrom_into(CHIP_ADDRESS, buff3, start=0, end=5)
# Continue reading change status address until /change pin goes high
while (pin1.value==0):
    buff[0] = 2
    i2c.writeto(CHIP_ADDRESS, buff, False)
    i2c.readfrom_into(CHIP_ADDRESS, buff3, start=0, end=5)
i2c.unlock()

#Function to read the Key Press Registers
#Return value is a combination of both registers (3 and 4) which links with the values in the 'PianoKeys' class
def _readKeyPress():
    buff = bytearray(1)
    buff2 = bytearray(2)
    buff3 = bytearray(5)
    buff[0] = 2
    while not i2c.try_lock():
        pass
    i2c.writeto(CHIP_ADDRESS, buff)
    i2c.readfrom_into(CHIP_ADDRESS, buff3)

    # Address 3 is the addr for keys 0-7 (this will then auto move onto Address 4 for keys 8-15, both reads stored in buff2)
    buff[0] = 3
    i2c.writeto(CHIP_ADDRESS, buff)
    i2c.readfrom_into(CHIP_ADDRESS, buff2)
    i2c.unlock()

    # keyRegValue is a 4 byte number which shows which keys are pressed
    keyRegValue = (buff2[1] + (buff2[0]*256))

    return keyRegValue
    
#Function to determine if a piano key is pressed and returns a true or false output.
def keyIsPressed(key: PianoKeys):
    keyPressed = False

    if (key & _readKeyPress()) == key:
        keyPressed = True

    return keyPressed

def playAudioFile(filename):
    global audio
    wave_file = open(filename, "rb")
    wave = WaveFile(wave_file)
    audio.play(wave)
    while audio.playing:
        pass
    audio.stop()

while True:
    if keyIsPressed(PianoKeys.KEY_K9) is True:
        playAudioFile("middle-c.wav")
    if keyIsPressed(PianoKeys.KEY_K1) is True:
        playAudioFile("c#4.wav")
    if keyIsPressed(PianoKeys.KEY_K10) is True:
        playAudioFile("d4.wav")
    if keyIsPressed(PianoKeys.KEY_K2) is True:
        playAudioFile("d#4.wav")
    if keyIsPressed(PianoKeys.KEY_K11) is True:
       playAudioFile("e4.wav")
    if keyIsPressed(PianoKeys.KEY_K12) is True:
        playAudioFile("f4.wav")
    if keyIsPressed(PianoKeys.KEY_K3) is True:
        playAudioFile("f#4.wav")
    if keyIsPressed(PianoKeys.KEY_K13) is True:
        playAudioFile("g4.wav")
    if keyIsPressed(PianoKeys.KEY_K4) is True:
        playAudioFile("g#4.wav")
    if keyIsPressed(PianoKeys.KEY_K14) is True:
        playAudioFile("a5.wav")
    if keyIsPressed(PianoKeys.KEY_K5) is True:
        playAudioFile("a#5.wav")
    if keyIsPressed(PianoKeys.KEY_K6) is True:
        playAudioFile("b5.wav")
    if keyIsPressed(PianoKeys.KEY_K7) is True:
        playAudioFile("c5.wav")
    
    
    #if clue.button_a:
    #    playAudioFile("middle-c.wav")
    #if clue.button_b:
    #    playAudioFile("g4.wav")
    
    #playAudioFile("middle-c.wav")
    #playAudioFile("c#4.wav")
    #playAudioFile("d4.wav")
    #playAudioFile("d#4.wav")
    #playAudioFile("e4.wav")
    #playAudioFile("f4.wav")
    #playAudioFile("f#4.wav")
    #playAudioFile("g4.wav")
    #playAudioFile("g#4.wav")
    #playAudioFile("a5.wav")
    #playAudioFile("a#5.wav")
    #playAudioFile("b5.wav")
    #playAudioFile("c5.wav")
