import abc
from enum import Enum


class ProtcolMessage(Enum):
    ENQ = chr(133)  # <ENQ> in acsii + 128
    NULL = chr(128)  # <Null>: 0 + 128
    ACK = chr(134)  # 6 + 128
    CR = chr(141)  # 13 + 128


class CommandCode(Enum):
    SCAN = "G"
    PAUSE = "P"
    STOP = "S"
    HOME = "H"
    SLEW = '9'
    JOGFORWARD = "F"
    JOGREVERSE = "R"
    FASTERJOG = "Q"
    SLOWERJOG = "Z"
    SCANMODE = "B"
    UNITS = "U"
    BURSTFIRE = "L"
    NEXTPOSITION = "N"
    SHGRETURN = "C"
    SHGALIGN = "K"
    SHGFORWARD = "D"
    SHGREVERSE = "E"
    SHGJOGCRYSTAL = "I"
    SHGJOGPRISM = "J"


class Command(object):

    def __init__(self, cmd):
        self.cmd = cmd

    __metaclass__ = abc.ABCMeta

    @property
    def cmd(self):
        return self._cmd

    @cmd.setter
    def cmd(self, cmd):
        self._cmd = cmd

    def computeCheckSum(self, cmd):
        cksm = 0
        for letter in str(cmd):
            cksm += ord(letter)
        return chr((cksm & 15) + 96) + chr((int(cksm / 16) & 15) + 96)

    @abc.abstractmethod
    def toSerialFormat(self):
        return


class ControlCommand(Command):

    def toSerialFormat(self):
        return self.cmd.value

    def __init__(self, cmd):
        self.cmd = cmd


class BasicCommand(Command):

    def __init__(self, cmd):
        self.cmd = cmd

    def toSerialFormat(self):
        return self.cmd.value + self.computeCheckSum(self.cmd.value) + ProtcolMessage.CR.value
