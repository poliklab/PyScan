import UniversalLibrary as UL
import time 
"""
This class obejctfies the board and is resposbible
for reading the data using the unversial library
"""


class Board(object):
    """
    Args:
                    Device number: Card to be read from
                    Channel number: Active channel on desired card
    """

    def __init__(self, deviceNumber, channelNumber):

        self.deviceNumber = deviceNumber
        self.channelNumber = channelNumber

    def __str__(self):
        return "Dev" + str(self.deviceNumber) + "/avi" + str(self.channelNumber)

    def getChannelNumber(self):
        return self.channelNumber

    def getDeviceNumber(self):
        return self.deviceNumber
    """
	Args:
		Gain: Voltage amplifaction defualts to zero
	Return:
		voltageReading: Voltage as float read from card
	"""

    def readVoltage(self, gain=0):
        # Based on my understanding of the universal library source code and docs
        # The UL.AbIN gets inupt from the card and the cbtoEngUnits reads the
        # input as voltage
        voltageReadings = list()
        # print self.channelNumber
        for i in range(0, self.channelNumber+1):
            # if i ==1:
            #     voltage = 0 
            #     short = 0 
            # else:
            short = UL.cbAIn(self.getDeviceNumber(), i, gain)
            voltage = UL.cbToEngUnits(self.getDeviceNumber(), gain, short)
            voltageReadings.append(voltage)
            print str(short) + " " + str(voltage)
            # print UL.cbToEngUnits(self.getDeviceNumber(), 0, UL.cbAIn(
            #     self.getDeviceNumber(), 0, gain))
            # print UL.cbToEngUnits(self.getDeviceNumber(), 1, UL.cbAIn(
            #     self.getDeviceNumber(), 1, gain))
            time.sleep(.001)
        return voltageReadings
