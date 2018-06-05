from model import SerialInterface, Scanner
from commands import ProtcolMessage
from view import *
import Tkinter as tk
import time
import threading
from session import Session
import pdb
import tkFileDialog as filedialog
""""
Keybinding labels are hardcoded into the text of the button in view
If key bindings are changed in the cotroller be sure to update the view 
or visa versa  
"""


class PCScanController(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)
        container.grid()

        # Next 8 lines instantiate the menus and make them navigable
        self.frames = {}
        for F in (MainMenu, ConfigureMenu, StartMenu, ScanMenu, ConfigureMenu, ControlMenu, DoublerMenu):
            page = F.__name__
            frame = F(master=container, controller=self)
            self.frames[page] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.protocol("WM_DELETE_WINDOW", self._quit)
        self.bindStartMenu()

        self.showFrame("StartMenu")

        # plain text gain specs mapped to the gain code defined in the UL documenation
        # and the the floor and ceiling as intergers
        # (code, floor, ceiling)
        self.gainDict = {
            "+/-5V": (0, -5, 5), "+/-10V": (1, -10, 10), "0-10V": (100, 0, 10)}

        # Dictionary for each menu that maps actions to keys
        self.configKeys = dict()
        self.controlKeys = dict()
        self.scanKeys = dict()

        self.controlKeys.update(
            {self.frames["ControlMenu"].jogContinFBut: "<f>"})
        self.controlKeys.update(
            {self.frames["ControlMenu"].jogContinRBut: "<r>"})
        self.controlKeys.update({self.frames["ControlMenu"].unitBut: "<u>"})
        self.controlKeys.update({self.frames["ControlMenu"].slewBut: "<l>"})
        self.controlKeys.update(
            {self.frames["ControlMenu"].calibrateBut: "<c>"})
        self.controlKeys.update({self.frames["ControlMenu"].stopBut: "<s>"})

        self.scanKeys.update({self.frames["ScanMenu"].scanBut: "<c>"})
        self.scanKeys.update({self.frames["ScanMenu"].pauseBut: "<p>"})
        self.scanKeys.update({self.frames["ScanMenu"].stopBut: "<s>"})
        self.scanKeys.update({self.frames["ScanMenu"].resumeBut: "<r>"})
        self.scanKeys.update({self.frames["ScanMenu"].saveBut: "<t>"})

        # Maps functions to a tuple of key and button

        self.configKeys.update(
            {self.frames["ConfigureMenu"].channelBut: "<n>"})
        self.configKeys.update(
            {self.frames["ConfigureMenu"].delayBut: "<d>"})
        self.configKeys.update(
            {self.frames["ConfigureMenu"].stopPosBut: "<f>"})
        self.configKeys.update(
            {self.frames["ConfigureMenu"].startPosBut: "<t>"})
        self.configKeys.update(
            {self.frames["ConfigureMenu"].scanIncBut: "<i>"})

        self.controlEnableList = list()
        self.controlEnableList.append(self.frames["ControlMenu"].jogContinFBut)
        self.controlEnableList.append(self.frames["ControlMenu"].jogContinRBut)
        self.controlEnableList.append(self.frames["ControlMenu"].slewBut)
        self.controlEnableList.append(self.frames["ControlMenu"].unitBut)
        self.controlEnableList.append(self.frames["ControlMenu"].calibrateBut)
        self.saveFlag = 0
        self.scanUnit = None
        self.pauseThread = False
        self.dataView = None

        self.floor = 15000
        self.ceiling = 15100
        self.limitsFlag = False
    """
    Args:
        page: frame to be disaplayed  
    
    Updates view to show the next frame  
    """

    def showFrame(self, page):
        frame = self.frames[page]
        frame.tkraise()
        # Focus needs to be set on the current frame so that tk can listen to
        # the keyboard
        frame.focus_set()
    """
        Binds tk buttons  with functions.
        Bind tk keyboard listeners with functions. 
    """

    def bindStartMenu(self):
        self.frames["StartMenu"].yesButton.configure(
            command=lambda: self.yesLaser())
        self.frames["StartMenu"].noButton.configure(
            command=lambda: self.noLaser())
        self.frames["StartMenu"].bind("<y>", lambda y: self.yesLaser())
        self.frames["StartMenu"].bind("<n>", lambda n: self.noLaser())
    """
        Only implement frames that dont require using the laser
    """

    def noLaser(self):
        self.frames["MainMenu"].setUp.configure(state="disabled")
        self.frames["MainMenu"].control.configure(state="disabled")
        self.frames["MainMenu"].scan.configure(state="disabled")
        self.showFrame("MainMenu")
    """
        Implement all frames and initialise some basic labels
        Creates Scanner object
        Binds menus and keyboard listeners
    """

    def yesLaser(self):

        self.readSettings()
        self.scanUnit = Scanner(float(self.scanInc), self.floor, self.ceiling)

        self.frames["ControlMenu"] .posTxt.configure(
            text=str(self.scanUnit.currentPosition) + " " + self.scanUnit.currentUnits)
        self.frames["ScanMenu"].posTxt.configure(
            text=str(self.scanUnit.currentPosition) + " " + self.scanUnit.currentUnits)
        self.updateConfigDisplay()
        self.updateScanMenuDisplay()
        self.bindControlMenu()
        self.bindConfigureMenu()
        self.bindScanMenu()
        self.showFrame("MainMenu")

    #-----------------General Model Control Methods---------------------------
    """
    Args: 
        direction: either "forward" or "reverse" 
        Ack instrument continually while jogging or slewing and update postion
   """

    def movePosition(self, direction):
        while getattr(self.moveThread, "move_run", True):
            self.scanUnit.ack()
            self.updatePositionLabel()
            if self.inBounds(direction) is True:
                self.scanUnit.stop()
                self.scanUnit.ack()
                self.frames["ControlMenu"].posTxt.configure(
                    text=str(self.scanUnit.currentPosition) + " " + self.scanUnit.currentUnits)
                self.enableControlButtons()
                return
             # print "Active threads"+ str(threading.enumerate())
            time.sleep(.1)
    """
        Updaye the postion label.
        Used both in the scan and control menu 
    """

    def updatePositionLabel(self):
        # print "updated label: ", str(self.scanUnit.currentPosition)
        self.frames["ControlMenu"].posTxt.configure(
            text=str(self.scanUnit.currentPosition) + " " + self.scanUnit.currentUnits)

    """
    Args: 
        direction: either "forward" or "reverse" 
    If posistion exceeds hard coded instrument bounds
    ToDo:
        Postion bounds read in from config file
    """

    def inBounds(self,  direction):
        position = self.scanUnit.currentPosition
        if direction == "Forward":
            if position >= self.ceiling:
                print "Instrument ceiling exceeded"
                print "Stopping thread"
                return True
            else:
                return False
        elif direction == "Reverse":
            if position <= self.floor:
                print "Instrument floor exceeded"
                print "Stopping thread"
                return True
            else:
                return False

    #--------------Control Menu-----------------------------------------------
    def bindControlMenu(self):
        """
        self.controlKeys = dict()
        self.controlKeys.update(
            {(self.frames["ControlMenu"].jogContinFBut: "<f>")})
        self.controlKeys.update(
            {self.frames["ControlMenu"].jogContinRBut: "<r>"})
        self.controlKeys.update({self.frames["ControlMenu"].unitBut: "<u>"})
        self.controlKeys.update({self.frames["ControlMenu"].slewBut: "<l>"})
        self.controlKeys.update(
            {self.frames["ControlMenu"].calibrateBut: "<c>"})
        self.controlKeys.update({self.frames["ControlMenu"].stopBut: "<s>"})
        self.configKeys.update(
            {self.frames["ConfigureMenu"].scanIncBut: "<i>"})
        self.configKeys.update({self.frames["ConfigureMenu"].delayBut: "<d>"})
        self.configKeys.update(
            {self.frames["ConfigureMenu"].stopPosBut: "<t>"})
        self.configKeys.update(
            {self.frames["ConfigureMenu"].startPosBut: "<f>"})
        """
        self.frames["ControlMenu"].unitBut.configure(
            command=self.changeUnits)
        self.frames["ControlMenu"].bind(
            self.controlKeys[self.frames["ControlMenu"].unitBut], lambda U: self.changeUnits())
        self.frames["ControlMenu"].jogContinFBut.configure(
            command=self.jogForward)
        self.frames["ControlMenu"].bind(
            self.controlKeys[self.frames["ControlMenu"].jogContinFBut], lambda F: self.jogForward())
        self.frames["ControlMenu"].jogContinRBut.configure(
            command=self.jogReverse)
        self.frames["ControlMenu"].bind(
            self.controlKeys[self.frames["ControlMenu"].jogContinRBut], lambda R: self.jogReverse())
        self.frames["ControlMenu"].stopBut.configure(command=self.stop)
        self.frames["ControlMenu"].bind(
            self.controlKeys[self.frames["ControlMenu"].stopBut], lambda S: self.stop())
        self.frames["ControlMenu"].slewBut.configure(command=self.slew)
        self.frames["ControlMenu"].bind(
            self.controlKeys[self.frames["ControlMenu"].slewBut], lambda L: self.slew())
        self.frames["ControlMenu"].back.configure(
            command=lambda: self.showFrame("MainMenu"))

    def disableControlButtons(self):
        for button in self.controlEnableList:
            button.config(state="disabled")

    def enableControlButtons(self):
        for button in self.controlEnableList:

            button.config(state="normal")
    """
        Switch instrument units: wavelength or wavenumbers
        Logic contained in the model
    """

    def changeUnits(self):
        self.scanUnit.changeUnits()
        self.frames["ControlMenu"].posTxt.configure(
            text=str(self.scanUnit.currentPosition) + " " + self.scanUnit.currentUnits)
    """
        Kill old thread if one exists 
        Start a new thread and update the postion and check the bounds 
        Kill thread when bounds met or move stopped
        
        For jogForward and jod Reverse its very important that only one thread is 
        commincateing to the serial prt 
    """

    def jogForward(self):
        if self.inBounds("Forward") is False:
            if hasattr(self, "scanThread") and self.scanThread is not None:
                print "Stopping thread"
                self.scanThread.scan_run = False
                self.scanUnit.stop()
            if hasattr(self, "moveThread") and self.moveThread is not None:
                print "Stopping thread"
                self.moveThread.move_run = False
                self.moveThread.join()
                self.scanUnit.stop()
            self.scanUnit.jogForward()
            self.moveThread = threading.Thread(
                target=lambda: self.movePosition("Forward"))
            self.disableControlButtons()
            self.moveThread.start()

    """
       Kill old thread if one exists 
       Start a new thread and update the postion and check the bounds 
       Write to insturment using model 
       Kill thread when bounds met or move stopped
   """

    def jogReverse(self):
        if self.inBounds("Reverse") is False:
            if hasattr(self, "scanThread") and self.scanThread is not None:
                print "Stopping thread"
                self.scanThread.scan_run = False
                self.scanUnit.stop()
            if hasattr(self, "moveThread") and self.moveThread is not None:
                print "Stopping thread"
                self.moveThread.move_run = False
                self.moveThread.join()
                self.scanUnit.stop()
            self.moveThread = threading.Thread(
                target=lambda: self.movePosition("Reverse"))
            self.disableControlButtons()
            self.scanUnit.jogReverse()
            self.moveThread.start()

    """
        Gerneic all stop for slewing, jogging, and scanning.
        Kills all threads, updates gui, and re-enables user control 
    """

    def stop(self):

        if hasattr(self, "scanThread") and self.scanThread is not None:
            print "Stopping thread"
            self.scanThread.scan_run = False
        if hasattr(self, "moveThread") and self.moveThread is not None:
            print "Stopping thread"
            self.moveThread.move_run = False
            self.moveThread.join()
            self.scanUnit.stop()
        self.scanUnit.stop()
        self.scanUnit.ack()
        self.frames["ControlMenu"].posTxt.configure(
            text=str(self.scanUnit.currentPosition) + " " + self.scanUnit.currentUnits)
        self.enableControlButtons()
    """
        Get slew postion from dialog box 
        ind helper controls to dialog box 
        Slew using model 
        Kills dialog box when finsihed 
    TODO: Input validation for slew postion 
    """

    def slew(self):
        self.disableControlButtons()
        dialogWindow = EntryBox("Slew to:")
        # Helper fucntion to make the lambda calculus easier :)

        def getSlewPos():
            position = float(dialogWindow.textEntry.get())
            if position > self.floor and position < self.ceiling:
                
                self.scanUnit.slew(position)
            else:    
                print self.floor
                print self.ceiling
                print "Entered position is now outside of bounds"
            dialogWindow.destroy()
        dialogWindow.yesButton.configure(
            command=lambda: getSlewPos())
        dialogWindow.bind("<Return>", lambda d: getSlewPos())
    #--------------Scan Menu--------------------------------------------------

    def bindScanMenu(self):

        self.frames["ScanMenu"].scanBut.configure(
            command=lambda: self.scanStart())
        self.frames["ScanMenu"].bind(
            self.scanKeys[self.frames["ScanMenu"].scanBut], lambda S: self.scanStart())
        self.frames["ScanMenu"].stopBut.configure(command=self.stop)
        self.frames["ScanMenu"].bind(
            self.scanKeys[self.frames["ScanMenu"].stopBut], lambda N: self.stop())
        self.frames["ScanMenu"].pauseBut.configure(command=self.pause)
        self.frames["ScanMenu"].bind(
            self.scanKeys[self.frames["ScanMenu"].pauseBut], lambda P: self.pause())
        self.frames["ScanMenu"].resumeBut.configure(
            command=lambda: self.resume())
        self.frames["ScanMenu"].bind(
            self.scanKeys[self.frames["ScanMenu"].resumeBut], lambda R: self.resume())
        self.frames["ScanMenu"].back.configure(
            command=lambda: self.showFrame("MainMenu"))
        self.bind("<Escape>", lambda back: self.showFrame("MainMenu"))
        self.frames["ScanMenu"].bind(
            self.scanKeys[self.frames["ScanMenu"].saveBut], lambda T: self.save())
        self.frames["ScanMenu"].saveBut.configure(command=self.save)

    """
        Set up windows and gui elements for a scan 
        Write intial scan options to intsument using the modle 
        
    """

    def scanStart(self):

        if self.dataView is not None:
            self.dataView.destroy()
        self.session = Session(0, int(self.channels),
                               self.gainDict[self.gain][0])
        self.dataView = ReadingWindow()  # Contains the plot
        startScanDialog = ScanStartBox()
        self.scanThread = threading.Thread(target=lambda: self.scan())

        self.scanUnit.setUpScan(self.startPos, self.stopPos,
                                self.scanInc)
        # BUG: for some reason the ReadingWindow focus.
        # The ScanDialog needs to have the focus instead
        startScanDialog.focus_set()
        startScanDialog.focus_force()

        startScanDialog.bind(
            "<Return>", lambda X: [self.scanThread.start(), startScanDialog.destroy()])
        startScanDialog.yesButton.configure(
            command=lambda: [self.scanThread.start(), startScanDialog.destroy()])
    """
        Reset data and limits of the polot and redraw 
        with newly buffered data
    """

    def drawPlot(self):
        self.dataView.plot.ax.clear()
        self.dataView.plot.ax.set_ylim(
            [self.gainDict[self.gain][1], self.gainDict[self.gain][2]])
        self.dataView.plot.ax.set_xlim([int(self.startPos), int(self.stopPos)])
        for i in range(0, int(self.channels) + 1):
            self.dataView.plot.ax.plot(
                self.session.xBuffer, self.session.yBuffer[i], linewidth=1)
        self.dataView.plot.draw()

    def scan(self):
        self.saveFlag = 1
        time.sleep(.5)
        max = (float(self.stopPos) - float(self.startPos)) * \
            (1 / float(self.scanInc))
        print "max: ", max
        i = 0
        position = float(self.startPos)
        while getattr(self.scanThread, "scan_run", True):
            if self.pauseThread == True:
                time.sleep(.5)
            else:
                time.sleep(float(self.delay))
                self.session.record(position)
                self.drawPlot()
                self.scanUnit.scan()
                # Take measurment
                if i == max:
                    print "Stop pos reached"
                    self.session.printBuffer()
                    self.save()
                    self.stop()

                    break
                i += 1
                position = position + float(self.scanInc)

    def save(self):
        if self.saveFlag == 1:
            print "Saving...."
            self.fileName = tkFileDialog.asksaveasfilename(
                initialdir=".", title="Select save file or cancel.", filetypes=((".csv files", "*.csv"), ("all files", "*.*")))
            if self.fileName is not None:
                self.session.saveSession(
                    self.fileName, self.scanUnit.currentUnits)
            # TODO: log file save
        else:
            pass

    def next(self):

        self.scanUnit.next()
        self.frames["ScanMenu"].posTxt.configure(
            text=str(self.scanUnit.currentPosition + float(self.scanInc)) + " " + self.scanUnit.currentUnits)

    def pause(self):
        self.pauseThread = True

    def resume(self):
        self.pauseThread = False
    #--------------Configure Menu---------------------------------------------

    def bindConfigureMenu(self):
        # Overwite defualt drop down options defined in the view
        self.frames["ConfigureMenu"].gainDropDown.children[
            "menu"].delete(0, "end")
        for value in self.gainDict.keys():
            self.frames["ConfigureMenu"].gainDropDown.children["menu"].add_command(
                label=value, command=lambda gainValue=value: self.setGain(gainValue))

        self.frames["ConfigureMenu"].startPosBut.configure(
            command=self.setStartPos)
        self.frames["ConfigureMenu"].bind(self.configKeys[self.frames[
            "ConfigureMenu"].startPosBut], lambda f: self.setStartPos())
        self.frames["ConfigureMenu"].stopPosBut.configure(
            command=self.setStopPos)
        self.frames["ConfigureMenu"].bind(self.configKeys[self.frames[
                                          "ConfigureMenu"].stopPosBut], lambda s: self.setStopPos())
        self.frames["ConfigureMenu"].scanIncBut.configure(
            command=self.setScanInc)
        self.frames["ConfigureMenu"].bind(self.configKeys[self.frames[
                                          "ConfigureMenu"].scanIncBut], lambda i: self.setScanInc())
        self.frames["ConfigureMenu"].delayBut.configure(
            command=self.setDelay)

        self.frames["ConfigureMenu"].bind(
            self.configKeys[self.frames["ConfigureMenu"].delayBut], lambda d: self.setDelay())
        self.frames["ConfigureMenu"].channelBut.configure(
            command=self.setNumberOfChannels)
        self.frames["ConfigureMenu"].bind(
            self.configKeys[self.frames["ConfigureMenu"].channelBut], lambda n: self.setNumberOfChannels())
        self.frames["ConfigureMenu"].back.configure(
            command=lambda: self.showFrame("MainMenu"))
        self.bind("<Escape>", lambda back: self.showFrame("MainMenu"))

    """
		This function should be bound to the enter button for scanInc, startPos, stopPos, and delay 
		Also called when the scan and config menus are updated
    """

    def calculateScanTime(self):
        try:
            time = str(((abs(float(self.stopPos) -
                             float(self.startPos)) / float(self.scanInc)) + 1) * float(self.delay))
            self.frames["ScanMenu"].scanTimeTxt.configure(
                text=time + " seconds")
            self.frames["ConfigureMenu"].scanTimeTxt.configure(
                text=time + " seconds")
            print "Updating"
        except AtrributeError:
            print "Passing"
            return ""
    """
		These next several methods control updating the info displayed in  configure menu 
		An instance of the dialog box is created each time
	"""

    def setGain(self, gainLabel):
        self.gain = gainLabel
        self.frames["ScanMenu"].gainTxt.configure(text=self.gain)
        self.frames["ConfigureMenu"].gainTxt.configure(text=self.gain)

    def setStartPos(self):

        dialogWindow = EntryBox("Set starting position")
        dialogWindow.bind("<Return>", lambda r: [self.updateConfigScanFromDialog(dialogWindow, "startPos",  self.frames[
            "ConfigureMenu"].starPosTxt, self.frames["ScanMenu"].starPosTxt, self.scanUnit.currentUnits), self.calculateScanTime()])
        dialogWindow.yesButton.configure(
            command=lambda: [self.updateConfigScanFromDialog(dialogWindow, "startPos",  self.frames["ConfigureMenu"].starPosTxt, self.frames["ScanMenu"].starPosTxt, self.scanUnit.currentUnits), self.calculateScanTime()])

    def setStopPos(self):

        dialogWindow = EntryBox("Set stop position")
        dialogWindow.bind("<Return>", lambda r: [self.updateConfigScanFromDialog(dialogWindow, "stopPos",  self.frames[
            "ConfigureMenu"].stopPosTxt, self.frames["ScanMenu"].stopPosTxt, self.scanUnit.currentUnits), self.calculateScanTime()])
        dialogWindow.yesButton.configure(
            command=lambda: [self.updateConfigScanFromDialog(dialogWindow, "stopPos",  self.frames["ConfigureMenu"].stopPosTxt, self.frames["ScanMenu"].stopPosTxt, self.scanUnit.currentUnits), self.calculateScanTime()])

    def setScanInc(self):
        # Heleper function to update the models increment
        def updateScannerInterval():
            self.scanUnit.interval = float(self.scanInc)
        dialogWindow = EntryBox("Set scan increment")
        dialogWindow.bind("<Return>", lambda r: [self.updateConfigScanFromDialog(
            dialogWindow, "scanInc",  self.frames["ConfigureMenu"].scanIncTxt,  self.frames["ScanMenu"].scanIncTxt), self.calculateScanTime(), updateScannerInterval()])
        dialogWindow.yesButton.configure(
            command=lambda: [self.updateConfigScanFromDialog(dialogWindow, "scanInc",  self.frames["ConfigureMenu"].scanIncTxt,  self.frames["ScanMenu"].scanIncTxt), self.calculateScanTime(), updateScannerInterval()])

    def setDelay(self):
        dialogWindow = EntryBox("Set delay")
        dialogWindow.bind("<Return>", lambda r: [self.updateConfigScanFromDialog(
            dialogWindow, "delay",  self.frames["ConfigureMenu"].delayTxt,  self.frames["ScanMenu"].delayTxt), self.calculateScanTime()])
        dialogWindow.yesButton.configure(
            command=lambda: [self.updateConfigScanFromDialog(dialogWindow, "delay",  self.frames["ConfigureMenu"].delayTxt,  self.frames["ScanMenu"].delayTxt), self.calculateScanTime()])

    def setNumberOfChannels(self):
        dialogWindow = EntryBox("Set number of channels")
        dialogWindow.bind("<Return>", lambda r: self.updateConfigScanFromDialog(
            dialogWindow, "channels",  self.frames["ConfigureMenu"].channelTxt,  self.frames["ScanMenu"].channelTxt))
        dialogWindow.yesButton.configure(
            command=lambda: self.updateConfigScanFromDialog(dialogWindow, "channels",  self.frames["ConfigureMenu"].channelTxt,  self.frames["ScanMenu"].channelTxt))

    """
		This method creates instance variables that describe instrument configureation options and-
		Updates the info labels in both the scan menu  (label1) and the configuration menu (label2)

	"""

    def updateConfigScanFromDialog(self, dialog, variableName, label, label2,  units=None):
        value = str.strip(dialog.textEntry.get())
        # Set variableName to value from setting file or dialog window
        setattr(self, variableName, value)
        if units is None:
            label.configure(text=value)
            label2.configure(text=value)
        else:
            label.configure(text=value + units)
            label2.configure(text=value + units)
        dialog.destroy()
    """
		Simlar to updateConfigScanFromDialog but used only for setting config data from file
	"""

    def updateConfigDisplay(self):
        self.frames["ConfigureMenu"].delayTxt.configure(text=self.delay)
        self.frames["ConfigureMenu"].gainTxt.configure(text=self.gain)
        self.frames["ConfigureMenu"].starPosTxt.configure(
            text=self.startPos + self.scanUnit.currentUnits)
        self.frames["ConfigureMenu"].stopPosTxt.configure(
            text=self.stopPos + self.scanUnit.currentUnits)
        self.frames["ConfigureMenu"].scanIncTxt.configure(text=self.scanInc)
        self.frames["ConfigureMenu"].channelTxt.configure(text=self.channels)

        self.calculateScanTime()

    #--------------Auxillary Methods------------------------------------------
    def updateScanMenuDisplay(self):
        self.frames["ScanMenu"].delayTxt.configure(text=self.delay)
        self.frames["ScanMenu"].gainTxt.configure(text=self.gain)
        self.frames["ScanMenu"].starPosTxt.configure(text=self.startPos)
        self.frames["ScanMenu"].stopPosTxt.configure(text=self.stopPos)
        self.frames["ScanMenu"].scanIncTxt.configure(text=self.scanInc)
        self.frames["ScanMenu"].channelTxt.configure(text=self.channels)
        self.calculateScanTime()
    """
		Write to configuration setting to file to be used again 
	"""

    def writeSettings(self):
        varsDict = dict()
        varsDict.update({"gain": self.gain})
        varsDict.update({"channels": self.channels})
        varsDict.update({"delay": self.delay})
        varsDict.update({"scanInc": self.scanInc})
        varsDict.update({"stopPos": self.stopPos})
        varsDict.update({"startPos": self.startPos})
        # csv_columns = ["Var", "Value"]
        with open("scan_config.set", "w") as config_file:
            for entry in varsDict:
                config_file.write(entry + "," + str(varsDict[entry]) + "\n")

    def readSettings(self):
        with open("scan_config.set", "r") as config_file:
            for line in config_file.readlines():
                varName, value = line.split(",")
                setattr(self, varName, str.strip(value))
                print "Setting: " + varName + " = " + str.strip(value)
                # print "reading lines"

    def _quit(self):
        # Dont save settigns if there is no scan unit implemented
        # This only applies when in the start screen or when no laser was
        # seleted
        if self.scanUnit is not None:
            self.writeSettings()
        self.quit()
        self.destroy()

# Program starts here! main method
app = PCScanController()

app.mainloop()
