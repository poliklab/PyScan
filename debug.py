import argparse 

class DebugLogger(object):

    def __init__(self):
        pass

    @staticmethod
    def setDebug():
        parser = argparse.ArgumentParser()
        parser.add_argument("--debug", nargs="?", const = True , default = False , help="Run in debug mode")
        args = parser.parse_args()
        if args.debug is None:
        	return False
        else:
        	return True

    @staticmethod
    def logMessage(message):
        with open("debug_log.txt", "ab+") as debug_log:
            debug_log.write("Message: " + message + "\n")

    @staticmethod
    def logReply(reply):
        with open("debug_log.txt", "ab+") as debug_log:
            debug_log.write("Reply: " + reply + "\n")
