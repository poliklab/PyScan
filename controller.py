from model import SerialInterface, Scanner
from commands import ProtcolMessage
from view import *
import Tkinter as tk
import time
import threading
from session import Session
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

        self.configKeys.update(
            {self.frames["ConfigureMenu"].scanIncBut: "<i>"})
        self.configKeys.update({self.frames["ConfigureMenu"].delayBut: "<d>"})
        self.configKeys.update(
            {self.frames["ConfigureMenu"].stopPosBut: "<t>"})
        self.configKeys.update(
            {self.frames["ConfigureMenu"].startPosBut: "<f>"})

        self.configKeys.update(
            {self.frames["ConfigureMenu"].channelBut: "<n>"})

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
        Binds 
    """

    def bindStartMenu(self):
        self.frames["StartMenu"].yesButton.configure(
            command=lambda: self.yesLaser())
        self.frames["StartMenu"].noButton.configure(
            command=lambda: self.noLaser())
        self.frames["StartMenu"].bind("<y>", lambda y: self.yesLaser())
        self.frames["StartMenu"].bind("<n>", lambda n: self.noLaser())

    def noLaser(self):
        self.frames["MainMenu"].setUp.configure(state="disabled")
        self.frames["MainMenu"].control.configure(state="disabled")
        self.frames["MainMenu"].scan.configure(state="disabled")
        self.showFrame("MainMenu")

    def yesLaser(self):

        self.readSettings()
        self.scanUnit = Scanner(float(self.scanInc))

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
    #--------------Control Menu-----------------------------------------------

    def updatePositionLabel(self):
        while getattr(self.posThread, "pos_run", True):
            self.frames["ControlMenu"].posTxt.configure(
                text=str(self.scanUnit.currentPosition) + " " + self.scanUnit.currentUnits)
            
    def bindControlMenu(self):
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

    def changeUnits(self):
        self.scanUnit.changeUnits()
        self.frames["ControlMenu"].posTxt.configure(
            text=str(self.scanUnit.currentPosition) + " " + self.scanUnit.currentUnits)

    def jogForward(self):
        
        self.posThread = threading.Thread(target= lambda: self.updatePositionLabel())
        self.disableControlButtons()
        self.scanUnit.jogForward()
        self.posThread.start()

    def jogReverse(self):
        self.posThread = threading.Thread(target= lambda: self.updatePositionLabel())
        self.disableControlButtons()
        self.scanUnit.jogReverse()
        self.posThread.start()
    # Bind setters to configure menu

    def stop(self):
        self.scanUnit.stop()
        if hasattr(self, "scanThread") and self.scanThread is not None:
            print "Stopping thread"
            self.scanThread.scan_run = False
        if hasattr(self, "posThread") and self.posThread is not None:
            print "Stopping thread"
            self.posThread.pos_run = False

        
        
        self.frames["ControlMenu"].posTxt.configure(
            text=str(self.scanUnit.currentPosition) + " " + self.scanUnit.currentUnits)
        self.enableControlButtons()

    def slew(self):
        self.disableControlButtons()
        dialogWindow = EntryBox("Slew to:")
        # Helper fucntion to make the lambda calculus easier :)

        def getSlewPos():
            position = float(dialogWindow.textEntry.get())
            self.scanUnit.slew(position)
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
		Display the plot window and  
    """

    def scanStart(self):

        if self.dataView is not None:
            self.dataView.destroy()
        self.session = Session(0, int(self.channels),
                               self.gainDict[self.gain][0])
        self.dataView = ReadingWindow()
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

            self.fileName = tkFileDialog.asksaveasfilename(
                initialdir="/", title="Select save file or cancel.", filetypes=((".csv files", "*.csv"), ("all files", "*.*")))
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
