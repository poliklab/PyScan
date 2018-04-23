import serial
from commands import ProtcolMessage
import time



class SerialInterface(object):

    def __init__(self):
        self.device = serial.Serial(
            port="COM2", baudrate=9600, bytesize=serial.EIGHTBITS, stopbits=2)
        self.lastResponse = ""
        self.protected = False

    def computeCheckSum(self, cmd):
        # All most a carbon copy of the pascal algorithm in PSCAN38
        cksm = 0
        for letter in str(cmd):
            cksm += ord(letter)
        return chr((cksm & 15) + 96) + chr((int(cksm / 16) & 15) + 96)

    def execute(self, message):
        if self.protected is False:

            self.protected = True
            message = str(message)
            reply = ""
            enqCounter = 0
            replyCounter = 0
            self.device.flushInput()  # Flush input buffer to pervent overflow
            reply = ""
            while enqCounter < 450:  # Quit after reading 450 nulls or about 10 cycles
                recieved = self.device.read()

                if recieved == ProtcolMessage.ENQ.value:
                    # Write our message!
                    if message == ProtcolMessage.ACK.value:
                        self.device.write(message)
                    else:
                        final = message + \
                            self.computeCheckSum(message) + ProtcolMessage.CR.value
                        self.device.write(final)
                    break  # Move on to waiting the reply
                enqCounter += 1
            while replyCounter < 1200:  # Quit after reading 1200 characters with out a valid response
                recieved = self.device.read()
                # Ignore response if it is a NULL or ENQ
                if recieved != ProtcolMessage.NULL.value and recieved != ProtcolMessage.ENQ.value:
                    if recieved == chr(13):  # Carriage return. Has to be ASCII 13
                        print reply
                        self.lastResponse = reply
                        print message
                        self.parseReply(reply)
                        break
                    reply += recieved
                replyCounter += 1    
            self.protected = False 
        else:
            print "Protected: " + message


    def parseReply(self, reply):
        self.status = reply[0]  # First index is a status message
        self.units = reply[1]   # Second index is the current units
        # Rest of the message
        # Last two indexes are the checkum which is igored
        self.digits = float(str.strip(reply[2:-2]))



class Scanner(object):

    def __init__(self, interval):
        # TODO: Set floor and ceiling in a setting file
        self.floor = 14975 
        self.ceiling = 16000
        self.interval = interval
        self.serialInterface = SerialInterface()
        self.ack() # Get info from instument to intailize Scanner object 
        self.currentPosition = self.serialInterface.digits
        self.currentUnits = self.serialInterface.units
        if self.currentUnits == "D":  # Skip the degree units
            self.changeUnits()
        elif self.currentUnits == "N":
            self.flipBounds()
    
    # TODO: Rewrite to remove return statements      
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
        

    def setUpScan(self, startPos, stopPos, increment):
        self.stop()
        self.serialInterface.execute("1:" + startPos)
        self.serialInterface.execute("1")

        print self.serialInterface.lastResponse
        
        self.serialInterface.execute("2:" + stopPos)
        self.serialInterface.execute("2")
        
        print self.serialInterface.lastResponse

        self.serialInterface.execute("3:" + increment)
        self.serialInterface.execute("5:1")
        
        print self.serialInterface.lastResponse
        
        self.serialInterface.execute("G")
        time.sleep(1)
        

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
        # print "Interval", self.interval
        rounded = round(pos / self.interval, 0) * self.interval

        # print "Before", pos
        # print "Rounded", rounded
        return rounded
