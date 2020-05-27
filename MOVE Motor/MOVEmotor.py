import board
import digitalio
import busio
import math

# A module to simplify the driving o the motors on Kitronik :MOVE Motor buggy with the Adafruit CLUE dev board
#
# If you get "OSError: [Errno 19] Unsupported operation"
# then it is likely the I2C driver IC has not got power - either the power is switched off or the batteries are flat
#

#grab the I2C bus
i2c = busio.I2C(board.P19, board.P20)
#Some useful constants
CHIP_ADDR = const(0x62) # CHIP_ADDR is the standard chip address for the PCA9632, datasheet refers to LED control but chip is used for PWM to motor driver
MODE_1_REG_ADDR = const(0x00)
MODE_2_REG_ADDR = const(0x01)
MOTOR_OUT_ADDR = const(0x08) #MOTOR output register address
MODE_1_REG_VALUE = const(0x00) #setup to normal mode and not to respond to sub address
MODE_2_REG_VALUE = const(0x04)  #Setup to make changes on ACK, outputs set to open-drain
MOTOR_OUT_VALUE = const(0xAA)  #Outputs set to be controled PWM registers
#Register offsets for the motors
LEFT_MOTOR = const(0x04)
RIGHT_MOTOR = const(0x02)


#An initialisation function to setup the PCA chip correctly
def setupMotorDriver():
    buffer = bytearray(2)
    buffer[0] = MODE_1_REG_ADDR
    buffer[1] = MODE_1_REG_VALUE
    while not i2c.try_lock():
        pass
    i2c.writeto(CHIP_ADDR,buffer)
    buffer[0] = MODE_2_REG_ADDR
    buffer[1] = MODE_2_REG_VALUE
    i2c.writeto(CHIP_ADDR,buffer)
    buffer[0] = MOTOR_OUT_ADDR
    buffer[1] = MOTOR_OUT_VALUE
    i2c.writeto(CHIP_ADDR,buffer)
#end of setupMotorDriver()
    i2c.unlock()

#A couple of 'raw' speed functions for the motors.
# these functions expect speed -255 -> +255
def LeftMotor(speed):
    motorBuffer=bytearray(2)
    gndPinBuffer=bytearray(2)
    if(math.fabs(speed)>255):
        motorBuffer[1] = 255
    else:
        motorBuffer[1] = int(math.fabs(speed))
    gndPinBuffer[1] = 0x00
    if(speed >0):
        #going forwards
        motorBuffer[0] = LEFT_MOTOR
        gndPinBuffer[0] =LEFT_MOTOR +1
    else: #going backwards, or stopping
        motorBuffer[0] =LEFT_MOTOR +1
        gndPinBuffer[0] = LEFT_MOTOR
    while not i2c.try_lock():
        pass
    i2c.writeto(CHIP_ADDR,motorBuffer)
    i2c.writeto(CHIP_ADDR,gndPinBuffer)
    i2c.unlock()

#speed -255 -> +255
def RightMotor(speed):
    motorBuffer=bytearray(2)
    gndPinBuffer=bytearray(2)

    if(math.fabs(speed)>255):
        motorBuffer[1] = 255
    else:
        motorBuffer[1] = int(math.fabs(speed))
    gndPinBuffer[1] = 0x00

    if(speed >0):
        #going forwards
        motorBuffer[0] =RIGHT_MOTOR +1
        gndPinBuffer[0] = RIGHT_MOTOR
    else: #going backwards
        motorBuffer[0] = RIGHT_MOTOR
        gndPinBuffer[0] =RIGHT_MOTOR +1
    while not i2c.try_lock():
        pass
    i2c.writeto(CHIP_ADDR,motorBuffer)
    i2c.writeto(CHIP_ADDR,gndPinBuffer)
    i2c.unlock()

#A function that stops both motors, rather than having to call Left and Right with zero speed.
def StopMotors():
    stopBuffer=bytearray(2)
    stopBuffer[0] = LEFT_MOTOR
    stopBuffer[1] = 0x00
    while not i2c.try_lock():
        pass
    i2c.writeto(CHIP_ADDR,stopBuffer)
    stopBuffer[0] =LEFT_MOTOR +1
    i2c.writeto(CHIP_ADDR,stopBuffer)
    stopBuffer[0] =RIGHT_MOTOR
    i2c.writeto(CHIP_ADDR,stopBuffer)
    stopBuffer[0] =RIGHT_MOTOR +1
    i2c.writeto(CHIP_ADDR,stopBuffer)
    i2c.unlock()


