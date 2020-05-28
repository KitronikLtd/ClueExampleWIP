# MCP7940 RTC chip module.
# for use with Adafruit CLUE and Circuit Python
# Copyright (c) Kitronik Ltd 2019.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from adafruit_clue import clue

class KitronikRTC:
    initalised = False
    CHIP_ADDRESS = 0x6F 	
    RTC_SECONDS_REG = 0x00		
    RTC_MINUTES_REG = 0x01		
    RTC_HOURS_REG = 0x02			
    RTC_WEEKDAY_REG = 0x03		
    RTC_DAY_REG = 0x04			
    RTC_MONTH_REG = 0x05			
    RTC_YEAR_REG = 0x06			
    RTC_CONTROL_REG = 0x07		
    RTC_OSCILLATOR_REG = 0x08 	
    RTC_PWR_UP_MINUTE_REG = 0x1C
    START_RTC = 0x80
    STOP_RTC = 0x00
    ENABLE_BATTERY_BACKUP = 0x08
    currentSeconds = 0			
    currentMinutes = 0
    currentHours = 0
    decSeconds = 0
    decMinutes = 0
    decHours = 0

    def __init__(self):

        writeBuf = bytearray(2)
        readBuf = bytearray(1)
        readCurrentSeconds = 0
        readWeekDayReg = 0
        writeBuf[0] = self.RTC_SECONDS_REG
        while not clue._i2c.try_lock():
            pass
        clue._i2c.writeto(self.CHIP_ADDRESS, writeBuf)
        clue._i2c.readfrom_into(self.CHIP_ADDRESS,readBuf)
        readCurrentSeconds = readBuf[0]
        writeBuf[0] = self.RTC_CONTROL_REG
        writeBuf[1] = 0x43
        clue._i2c.writeto(self.CHIP_ADDRESS, writeBuf)
        writeBuf[0] = self.RTC_WEEKDAY_REG
        clue._i2c.writeto(self.CHIP_ADDRESS, writeBuf)
        clue._i2c.readfrom_into(self.CHIP_ADDRESS, readBuf)
        readWeekDayReg = readBuf[0]
        writeBuf[0] = self.RTC_WEEKDAY_REG
        writeBuf[1] = self.ENABLE_BATTERY_BACKUP | readWeekDayReg
        clue._i2c.writeto(self.CHIP_ADDRESS, writeBuf)
        writeBuf[0] = self.RTC_SECONDS_REG
        writeBuf[1] = self.START_RTC | readCurrentSeconds
        clue._i2c.writeto(self.CHIP_ADDRESS, writeBuf)
        clue._i2c.unlock()

    def readValue(self):
        writeBuf = bytearray(1)
        readBuf = bytearray(7)
        self.readCurrentSeconds = 0
        writeBuf[0] = self.RTC_SECONDS_REG
        while not clue._i2c.try_lock(): #grab the I2C bus
            pass
        clue._i2c.writeto(self.CHIP_ADDRESS, writeBuf)
        clue._i2c.readfrom_into(self.CHIP_ADDRESS,readBuf)
        clue._i2c.unlock() #remember to play nice and release the bus
        self.currentSeconds = (((readBuf[0] & 0x70) >> 4) * 10) + (readBuf[0] & 0x0F)
        self.currentMinutes = (((readBuf[1] & 0x70) >> 4) * 10) + (readBuf[1] & 0x0F)
        self.currentHours = (((readBuf[2] & 0x10) >> 4) * 10) + (readBuf[2] & 0x0F)
        self.currentWeekDay = readBuf[3]
        self.currentDay = (((readBuf[4] & 0x30) >> 4) * 10) + (readBuf[4] & 0x0F)
        self.currentMonth =(((readBuf[5] & 0x10) >> 4) * 10) + (readBuf[5] & 0x0F)
        self.currentYear = (((readBuf[6] & 0xF0) >> 4) * 10) + (readBuf[6] & 0x0F)

    # These read functions only return the last read values.
    # use readValue() to update the stored numbers
    # Done this way as only the seconds changes quickly, so could save I2C transactions.
    def readSec(self):
       return self.currentSeconds

    def readMin(self):
        return self.currentMinutes

    def readHrs(self):
        return self.currentHours

    def readDay(self):
       return self.currentDay

    def readWeekDay(self):
       return self.currentWeekDay

    def readMonth(self):
       return self.currentMonth

    def readYear(self):
       return self.currentYear

#
    def setTime(self, setHours, setMinutes, setSeconds):
        print("Set Time to ")
        print(setHours,":",setMinutes,":",setSeconds)
        writeBuf = bytearray(2)
        writeBuf[0] = self.RTC_SECONDS_REG
        writeBuf[1] = self.STOP_RTC
        while not clue._i2c.try_lock():
            pass
        clue._i2c.writeto(self.CHIP_ADDRESS, writeBuf)
        writeBuf[0] = self.RTC_HOURS_REG
        writeBuf[1] = (int(setHours / 10) << 4) | int(setHours % 10)	
        clue._i2c.writeto(self.CHIP_ADDRESS, writeBuf)
        writeBuf[0] = self.RTC_MINUTES_REG
        writeBuf[1] = (int(setMinutes / 10) << 4) | int(setMinutes % 10)
        clue._i2c.writeto(self.CHIP_ADDRESS, writeBuf)
        writeBuf[0] = self.RTC_SECONDS_REG
        writeBuf[1] = self.START_RTC |  (int(setSeconds / 10) << 4) | int(setSeconds % 10)
        clue._i2c.writeto(self.CHIP_ADDRESS, writeBuf)
        clue._i2c.unlock()


#end class KitronikRTC