import serial
from commands import *
 
# Based on specs given in SCU manual
ser = serial.Serial(port="COM2", baudrate=9600,
                    bytesize=serial.EIGHTBITS, stopbits=2, rtscts=True)

class DebugLogger(object):

    def __init__(self):
        pass
    
    @staticmethod
    def l1ogMessage(message):
        with open("debug_log_raw.txt", "ab+") as debug_log:
            debug_log.write("Message: " + message+"\n")

    @staticmethod
    def logReply(reply):
        print reply 
        with open("debug_log_raw.txt", "ab+") as debug_log:
            print "writing"
            debug_log.write("Reply: " + reply+"\n")

def computeCheckSum(cmd):
    # All most carbon copy of pascalalgorithm in PSCAN38
    cksm = 0
    for letter in str(cmd):
        cksm += ord(letter)
    return chr((cksm & 15) + 96) + chr((int(cksm / 16) & 15) + 96)


def execute(message):
    reply = ""
    enqCounter = 0
    replyCounter = 0
    ser.flushInput()
    while enqCounter < 145:  # Quit after reading 145 nulls
        recieved = ser.read()
        if recieved == ProtcolMessage.ENQ.value:
            final = message + computeCheckSum(message) + ProtcolMessage.CR.value
            #DebugLogger.logMessage(message)
            ser.write(final)
            break  # Move on to waiting the reply
        enqCounter += 1
    while replyCounter < 1200:  # Quit after reading 1200 charcters with out a valid response
        recieved = ser.read()
        # Ignore response if it is a NULL or ENQ
        if recieved != ProtcolMessage.NULL.value and recieved != ProtcolMessage.ENQ.value:
            if recieved == chr(13):  # Carraige return. Has to be ASCII 13
                #DebugLogger.logReply(reply)
                return reply[0:-2] #strip return checksum
            reply += recieved
        replyCounter += 1

while True:
    message = str.strip(raw_input("-->"))
    if message == "ACK":
        print execute(ProtcolMessage.ACK.value)
    else:
        print execute(message + computeCheckSum(message) + ProtcolMessage.CR.value)

