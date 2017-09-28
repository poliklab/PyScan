import serial
from commands import ProtcolMessage
import threading
import time
import argparse
from debug import DebugLogger


class SerialInterface (object):

    def __init__(self):
        self.debug = DebugLogger.setDebug()
        self.device = serial.Serial(
            port="COM2", baudrate=9600, bytesize=serial.EIGHTBITS, stopbits=2)
        self.lastResponse = ""

    def computeCheckSum(self, cmd):
        # All most a carbon copy of the pascal algorithm in PSCAN38
        cksm = 0
        for letter in str(cmd):
            cksm += ord(letter)
        return chr((cksm & 15) + 96) + chr((int(cksm / 16) & 15) + 96)

    def execute(self, message):
        # print message
        message = str(message)
        reply = ""
        enqCounter = 0
        replyCounter = 0
        self.device.flushInput()
        reply = ""
        while enqCounter < 450:  # Quit after reading 450 nulls or about 10 cycles
            recieved = self.device.read()

            if recieved == ProtcolMessage.ENQ.value:
                # Write our message!

                if message == ProtcolMessage.ACK.value:
                    DebugLogger.logMessage(message)
                    self.device.write(message)
                else:
                    final = message + \
                        self.computeCheckSum(message) + ProtcolMessage.CR.value
                    if self.debug == True:
                        DebugLogger.logMessage(message)
                    self.device.write(final)

                break  # Move on to waiting the reply
            enqCounter += 1
        while replyCounter < 1200:  # Quit after reading 1200 characters with out a valid response
            recieved = self.device.read()

            # Ignore response if it is a NULL or ENQ
            if recieved != ProtcolMessage.NULL.value and recieved != ProtcolMessage.ENQ.value:
                if recieved == chr(13):  # Carriage return. Has to be ASCII 13
                    if self.debug == True:
                        DebugLogger.logReply(reply)
                    # print reply
                    self.lastResponse = reply
                    self.parseReply(reply)
                    break
                reply += recieved
            replyCounter += 1

    def parseReply(self, reply):
        self.status = reply[0]  # First index is a status message
        self.units = reply[1]
        # Rest of the message with out the checksum
        self.digits = float(str.strip(reply[2:-2]))
        # print "Reply: " + str(self.digits)


class Scanner(object):

    def __init__(self, interval):
        self.floor = 14975
        self.ceiling = 16000
        self.interval = interval
        self.serialInterface = SerialInterface()
        self.ack()
        self.currentPosition = self.serialInterface.digits
        self.currentUnits = self.serialInterface.units
        if self.currentUnits == "D":  # Skip the degree units
            self.changeUnits()
        elif self.currentUnits == "N":
            self.flipBounds()
        self.t = None

    def slew(self, position):

        if position == self.currentPosition:
            return
        elif position > self.floor and position < self.ceiling:
            self.serialInterface.execute("9:" + str(position))
            self.updateStatus()
        else:
            print "Slew position out of bounds"
            return

    def ack(self):
        self.serialInterface.execute(ProtcolMessage.ACK.value)
        self.updateStatus()

    def changeUnits(self):
        self.serialInterface.execute("U")
        if self.serialInterface.units == "D":
            self.serialInterface.execute("U")
        self.flipBounds()
        self.updateStatus()

    def jogForward(self):

        if self.currentUnits == "W":
            self.serialInterface.execute("R")
        if self.currentUnits == "N":
            self.serialInterface.execute("F")

    def jogReverse(self):

        if self.currentUnits == "W":
            self.serialInterface.execute("F")
        if self.currentUnits == "N":
            self.serialInterface.execute("R")

    def updateStatus(self):
        self.currentPosition = self.roundPosition(
            float(self.serialInterface.digits))
        self.currentUnits = self.serialInterface.units

    def stop(self):
        self.serialInterface.execute("S")
        self.updateStatus()
        if self.t is not None:
            self.t.check_in_bounds = False

    def setUpScan(self, startPos, stopPos, increment):
        self.stop()
        # self.stop()
        # self.serialInterface.exec  ute("1:15000")
        self.serialInterface.execute("1:" + startPos)
        self.serialInterface.execute("1")
        print self.serialInterface.lastResponse
        self.serialInterface.execute("2:" + stopPos)
        self.serialInterface.execute("2")
        print self.serialInterface.lastResponse
        self.serialInterface.execute("3:" + increment)
        # print self.serialInterface.lastResponse
        # self.serialInterface.execute("4:19.86")
        # print self.serialInterface.lastResponse
        self.serialInterface.execute("5:1")
        print self.serialInterface.lastResponse
        # self.serialInterface.execute("6:.0")
        # print self.serialInterface.lastResponse
        self.serialInterface.execute("G")
        time.sleep(1)
        # print self.serialInterface.lastResponse

    def scan(self):
        self.serialInterface.execute("N")
        self.updateStatus()

    def pause(self):
        self.serialInterface.execute("P")
        self.updateStatus()

    def coverntUnits(self, value):
        return float(10000000) / value  # TODO: imporve conversion

    def flipBounds(self):

        ceiling = self.coverntUnits(self.floor)
        floor = self.coverntUnits(self.ceiling)
        self.floor = floor
        self.ceiling = ceiling

    def roundPosition(self, pos):
        print "Interval", self.interval
        rounded = round(pos / self.interval, 0) * self.interval
        print "Before", pos
        print "Rounded", rounded
        return rounded
