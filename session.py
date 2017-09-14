
from board import Board
from datetime import datetime

import time
import threading


"""
This class repersents a measurement session. It trackes voltage data,
and position 

"""


class Session(object):
    """
    Args:
        channels: max channels numbers 
        device: device number

    """

    def __init__(self, device, channels,  gain):

        self.channels = channels
        self.gain = gain
        self.board = Board(device, self.channels)
        self.xBuffer = list()
        self.yBuffer = list()
        for i in range(0, self.channels + 1):
            self.yBuffer.append(list())

    def __str__(self):
        return "Session run on " + str(self.board)

    """"
	This is most important function in the clas
	This method is designed to run as thread sperate from the gui
	So the plot can always be updating in the background

	"""

    def record(self, position):
        self.updateSession(position,
                           self.board.readVoltage(self.gain))

    """
		Updates the plots and data buffers with each mesurement
		Helper function for runSession
	"""

    def updateSession(self, x, y):

        self.xBuffer.append(x)

        for i in range(0, self.channels + 1):
            print i
            self.yBuffer[i].append(y[i])
        # print y
        # print "%f.2 , %f.4" % (self.xBuffer[-1], self.yBuffer[-1])

    # This prints the data for debugging
    def printBuffer(self):
        for i in range(len(self.xBuffer)):
            formatedReading = ""
            formatedReading = " %.2f :" % (self.xBuffer[i])
            for j in range(0, self.channels + 1):
                formatedReading = formatedReading + \
                    " %.2f, " % (self.yBuffer[j][i])
                # if j == self.channels:
            print formatedReading

    """
	Write the data out as a .csv with a brief header
	Args:
		saveFile: File object given by the broswer in the view/controller
        units: either wavelength or wavenumbers passed from 
        the controller after being read from the intrument 
        via the serial model  
	"""

    def saveSession(self, saveFile, units):
        saveFile = open(saveFile, 'w')
        saveFile.write(str(self))
        saveFile.write("Date/Time:" + str(datetime.now()) + "\n")
        saveFile.write("Position(" + units + ",) Signal(V)\n")

        #saveFile.write("Position, Voltage(" + units +  ")\n")
        channelString = ""
        for i in range(0,  self.channels+1):
            channelString = channelString + "Channel " + str(i) + ","
            if i == self.channels + 1:
                channelString = channelString + "Channel " + i 
        saveFile.write(channelString+"\n") 
        for i in range(len(self.xBuffer)):
            formatedReading = ""
            formatedReading = " %.2f :" % (self.xBuffer[i])
            for j in range(0, self.channels + 1):
                formatedReading = formatedReading + \
                    " %.2f, " % (self.yBuffer[j][i])
                if j == self.channels:
                    formatedReading = formatedReading + \
                    " %.2f " % (self.yBuffer[j][i])
            saveFile.write(formatedReading + "\n")
