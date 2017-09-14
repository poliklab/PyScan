import Tkinter as tk
import Tkinter, Tkconstants, tkFileDialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class StartMenu(tk.Frame):

    def __init__(self, controller, master=None):
        tk.Frame.__init__(self, master)
        self.controller = controller
        self.grid()
        title = tk.Label(self, text="PCscanPY")
        question = tk.Label(self, text="Implement Laser?")
        self.yesButton = tk.Button(
            self, text="Yes <y>")
        self.noButton = tk.Button(
            self, text="No <n>",)

        logoImage = tk.PhotoImage(file="pcscan_logo.gif")
        logo = tk.Label(self, image=logoImage)
        logo.image = logoImage
        logo.grid(row=1, column=2)
        #title.grid(row=1, column=2)
        question.grid(row=2, column=2)
        self.yesButton.grid(row=3, column=1)
        self.noButton.grid(row=3, column=3)
        self.bind("<Escape>", lambda quit: self.quit())


class MainMenu(tk.LabelFrame):

    def __init__(self, controller, master=None):
        tk.LabelFrame.__init__(self, master, text="Main Menu")
        self.controller = controller
        self.grid()

        self.setUp = tk.Button(self, text="Configure Acquisition <c>",
                               command=lambda: controller.showFrame("ConfigureMenu"))
        self.bind("<c>", lambda c: controller.showFrame("ConfigureMenu"))
        self.control = tk.Button(self, text="Control Laser <l>",
                                 command=lambda: controller.showFrame("ControlMenu"))
        self.bind("<l>", lambda l: controller.showFrame("ControlMenu"))
        self.scan = tk.Button(self, text="Scan Laser <s>",
                              command=lambda: controller.showFrame("ScanMenu"))
        self.bind("<s>", lambda s: controller.showFrame("ScanMenu"))
        self.store = tk.Button(self, text="Store to Disk")
        self.load = tk.Button(self, text="Load to Disk")
        self.view = tk.Button(self, text="View Data Set")
        self.doubler = tk.Button(self, text="Control Doubler",
                                 command=lambda: controller.showFrame("DoublerMenu"))
        self.quitBut = tk.Button(self, text="Quit <ESC>")

        self.setUp.grid()
        self.control.grid()
        self.scan.grid()
        self.store.grid()
        self.load.grid()
        self.view.grid()
        self.doubler.grid()
        self.quitBut.grid()

        self.bind("<Escape>", lambda q: self.quit())


class ConfigureMenu(tk.LabelFrame):

    def __init__(self, controller, master=None):
        tk.LabelFrame.__init__(self, master, text="Configure Acquisition Menu")
        self.controller = controller
        self.grid()

        # Set up frames
        optionsFrame = tk.LabelFrame(self, text="Options")
        paramFrame = tk.LabelFrame(self, text=" Scan Parameters")
        gainFrame = tk.Frame(paramFrame)
        optionsFrame.grid(row=1, column=1)
        paramFrame.grid(row=1, column=2)
        # Generic options for the gain drop down menu
        # Will be overwritten in the controller 
        variable = tk.StringVar(self)
        variable.set("")

        # Option Buttons
        self.back = tk.Button(optionsFrame, text="Back to Main Menu <ESC>")
        self.startPosBut = tk.Button(
            optionsFrame, text="Set Starting Position <f>")

        self.stopPosBut = tk.Button(
            optionsFrame, text="Set Stopping Position <t>")
        self.scanIncBut = tk.Button(
            optionsFrame, text="Set Scan Increment <i>")
        self.delayBut = tk.Button(
            optionsFrame, text="Set Delay between Increments <d>")
        self.channelBut = tk.Button(
            optionsFrame, text=" Set Number of Channels <n>")
        self.channelAsgnBut = tk.Button(
            optionsFrame, text="Assign Channel Names ")
        # Parameter Labels and data
        self.startPosLab = tk.Label(paramFrame, text="Starting Position:")
        self.starPosTxt = tk.Label(paramFrame, text="")
        self.stopPosLab = tk.Label(paramFrame, text="Stopping Position:")
        self.stopPosTxt = tk.Label(paramFrame, text="")
        self.scanIncLab = tk.Label(paramFrame, text="Size of Increment:")
        self.scanIncTxt = tk.Label(paramFrame, text="")
        self.delayLab = tk.Label(paramFrame, text=" Increment Delay:")
        self.delayTxt = tk.Label(paramFrame, text="")
        self.gainLab = tk.Label(paramFrame, text = "Gain:")
        self.channelLab = tk.Label(paramFrame, text="Number of Channels:")
        self.channelTxt = tk.Label(paramFrame, text="")
        self.scanTimeLab = tk.Label(paramFrame, text="Est. Scan Time:")
        self.scanTimeTxt = tk.Label(paramFrame, text="")
        self.channelNameLab = tk.Label(paramFrame, text="Channel name:")
        self.channelNameTxt = tk.Label(paramFrame, text="")

        self.gainTxt = tk.Label(gainFrame, text = "")
        self.gainDropDown = tk.OptionMenu(gainFrame, variable, "")
        # Grid everying into their respective frames
        self.back.grid()
        self.startPosBut.grid()
        self.stopPosBut.grid()
        self.scanIncBut.grid()
        self.delayBut.grid()
        self.channelBut.grid()
        self.channelAsgnBut.grid()
        self.startPosLab.grid()
        self.starPosTxt.grid()
        self.stopPosLab.grid()
        self.stopPosTxt.grid()
        self.scanIncLab.grid()
        self.scanIncTxt.grid()
        self.delayLab.grid()
        self.delayTxt.grid()
        self.gainLab.grid()
        self.gainTxt.grid(row = 1, column=1)
        self.gainDropDown.grid(row =1 ,column=2)
        gainFrame.grid()
        self.gainTxt.grid()
        self.channelLab.grid()
        self.channelTxt.grid()
        self.scanTimeLab.grid()
        self.scanTimeTxt.grid()
        self.channelNameLab.grid()
        self.channelNameTxt.grid()


class ControlMenu(tk.Frame):

    def __init__(self, controller, master=None):
        tk.Frame.__init__(self, master)
        self.controller = controller
        self.grid()

        optionsFrame = tk.LabelFrame(self, text="Options")
        paramFrame = tk.LabelFrame(self, text="Scan Parameters")

        optionsFrame.grid(row=1, column=1)
        paramFrame.grid(row=1, column=2)

        self.back = tk.Button(optionsFrame, text="Back to Main Menu <Esc>")
        self.jogOneFBut = tk.Button(optionsFrame, text="Jog One Step Forward")
        self.jogOneRBut = tk.Button(optionsFrame, text="Jog One Step Backward")
        self.jogContinFBut = tk.Button(
            optionsFrame, text="Jog Forward Continuously <f>")
        self.jogContinRBut = tk.Button(
            optionsFrame, text="Jog Backward Continuously <r>")
        self.slewBut = tk.Button(optionsFrame, text="Slew to New Position <l>")
        self.calibrateBut = tk.Button(optionsFrame, text="Calibrate Position")
        self.unitBut = tk.Button(optionsFrame, text="Change Units <u>")
        self.orderBut = tk.Button(optionsFrame, text="Set Order")
        self.stopBut = tk.Button(optionsFrame, text="Stop <s>")
        self.posLab = tk.Label(paramFrame, text="Position:")
        self.orderLab = tk.Label(paramFrame, text="Order:")
        self.posTxt = tk.Label(paramFrame, text="")
        self.orderTxt = tk.Label(paramFrame, text="")

        self.jogOneFBut.grid()
        self.jogOneRBut.grid()
        self.jogContinFBut.grid()
        self.jogContinRBut.grid()
        self.slewBut.grid()
        self.calibrateBut.grid()
        self.unitBut.grid()
        self.orderBut.grid()
        self.back.grid()
        self.posLab.grid()
        self.posTxt.grid()
        self.orderLab.grid()
        self.orderTxt.grid()
        self.stopBut.grid()

        self.bind("<Escape>", lambda back: controller.showFrame("MainMenu"))


class ScanMenu(tk.Frame):

    def __init__(self, controller, master=None):
        tk.Frame.__init__(self, master)
        self.controller = controller
        self.grid()
        optionsFrame = tk.LabelFrame(self, text="Options")
        paramFrame = tk.LabelFrame(self, text=" Scan Parameters")
        optionsFrame.grid(row=1, column=1)
        paramFrame.grid(row=1, column=2)

        self.back = tk.Button(optionsFrame, text="Back to Main Menu")
        self.scanBut = tk.Button(optionsFrame, text="Scan <c>")
        self.stopBut = tk.Button(optionsFrame, text="Stop <s>")
        self.pauseBut = tk.Button(optionsFrame, text="Pause <p>")
        self.resumeBut = tk.Button(optionsFrame, text = "Resume <r>")
        self.saveBut = tk.Button(optionsFrame, text = "Save <t>")
        # Parameter Labels and data
        self.currentPosLab = tk.Label(paramFrame, text="Current Position:")
        self.posTxt = tk.Label(paramFrame, text="")
        self.startPosLab = tk.Label(paramFrame, text="Starting Position:")
        self.starPosTxt = tk.Label(paramFrame, text="")
        self.stopPosLab = tk.Label(paramFrame, text="Stopping Position:")
        self.stopPosTxt = tk.Label(paramFrame, text="")
        self.scanIncLab = tk.Label(paramFrame, text="Size of Increment:")
        self.scanIncTxt = tk.Label(paramFrame, text="")
        self.delayLab = tk.Label(paramFrame, text=" Increment Delay:")
        self.delayTxt = tk.Label(paramFrame, text="")
        self.gainLab = tk.Label(paramFrame, text="Gain:")
        self.gainTxt = tk.Label(paramFrame, text="")
        self.channelLab = tk.Label(paramFrame, text="Number of Channels:")
        self.channelTxt = tk.Label(paramFrame, text="")
        self.scanTimeLab = tk.Label(paramFrame, text="Est. Scand Time:")
        self.scanTimeTxt = tk.Label(paramFrame, text="")
        self.channelNameLab = tk.Label(paramFrame, text="Channel name:")
        self.channelNameTxt = tk.Label(paramFrame, text="")

        self.currentPosLab.grid()
        self.posTxt.grid()
        self.startPosLab.grid()
        self.starPosTxt.grid()
        self.stopPosLab.grid()
        self.stopPosTxt.grid()
        self.scanIncLab.grid()
        self.scanIncTxt.grid()
        self.delayLab.grid()
        self.delayTxt.grid()
        self.gainLab.grid()
        self.gainTxt.grid()
        self.channelLab.grid()
        self.channelTxt.grid()
        self.scanTimeLab.grid()
        self.scanTimeTxt.grid()
        self.channelNameLab.grid()
        self.channelNameTxt.grid()

        self.scanBut.grid()
        self.stopBut.grid()
        self.pauseBut.grid()
        self.resumeBut.grid()
        self.saveBut.grid()
        self.back.grid()
        

        self.bind("<Escape>", lambda back: controller.showFrame("MainMenu"))


class DoublerMenu(tk.LabelFrame):

    def __init__(self, controller, master=None):
        tk.LabelFrame.__init__(self, master, text="Doubler Menu")
        self.controller = controller
        self.grid()
        back = tk.Button(self, text="Back to Main Menu",
                         command=lambda: controller.showFrame("MainMenu"))
        back.grid()

        self.bind("<Escape>", lambda back: controller.showFrame("MainMenu"))


class ReadingWindow(tk.Toplevel):

    def __init__(self,  master=None):
        print "Starting new reading window "
        tk.Toplevel.__init__(self, master)
        print "Created!"
        self.grid()
        self.plot = ScanPlot(self)
        self.plot.get_tk_widget().grid()

class ScanPlot(FigureCanvasTkAgg):
    def __init__(self, master):
        f = Figure()
        FigureCanvasTkAgg.__init__(self, f, master=master)
        self.ax = f.add_subplot(1, 1, 1)
        self.ax.set_autoscaley_on(False)  # Y fixed  


class EntryBox(tk.Toplevel):

    def __init__(self, message, master=None):
        tk.Toplevel.__init__(self, master)
        self.grid()
        self.textEntry = tk.Entry(self)
        self.yesButton = tk.Button(self, text="Enter <Return>")
        self.cancelButton = tk.Button(
            self, text="Cancel <ESC>", command=self.destroy)
        self.title = tk.Label(self, text=message)
        self.title.grid(row=1, column=2)
        self.textEntry.grid(row=2, column=2)
        self.yesButton.grid(row=3, column=1)
        self.cancelButton.grid(row=3, column=3)
        self.bind("<Escape>", lambda destroy: self.destroy())
        self.textEntry.focus_set()

class ScanStartBox(tk.Toplevel):

    def __init__(self,  master=None):
        tk.Toplevel.__init__(self, master)
        self.grid()
         
        self.yesButton = tk.Button(self, text="Enter <Return>")
        self.cancelButton = tk.Button(
            self, text="Cancel <ESC>", command=self.destroy)
        self.title = tk.Label(self, text="Hit enter to start scan")
        self.title.grid(row=1, column=2)
        
        self.yesButton.grid(row=3, column=1)
        self.cancelButton.grid(row=3, column=3)
        self.bind("<Escape>", lambda destroy: self.destroy())
        
