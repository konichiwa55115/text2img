import sys
import threading
from utils import logger
from utils.queue.queue import Queue
from input import Input

__logger = None
__input = None
__queue = None

class App():
    def __init__(self) -> None:
        try:
            self.__logger = logger.Logger()
            self.__input = Input()
            self.__queue = Queue()
        except Exception as exp:
            if hasattr(exp, 'message'):
                errorMessage = exp.message
            else:
                errorMessage = str(exp)

            print('Can not start App. Error: %s' % errorMessage)
            sys.exit()

    def run(self) -> None:
        self.__logger.log('App started')

        self.loop()

    """
    Main loop
    """
    def loop(self) -> None:
        try:
            handleInputsLoopThread = threading.Thread(target = self.handleInputsLoop)
            jobsLoopThread = threading.Thread(target = self.jobsLoop)

            handleInputsLoopThread.start()
            jobsLoopThread.start()
        except Exception as exp:
            self.__logger.logError(exp)

    """
    Handle inputs loop
    """
    def handleInputsLoop(self) -> None:
        self.__logger.log('Start hadle inputs')
        while True:
            try:
                self.__input.handleInputs() # handle inputs from telegram
            except Exception as exp:
                self.__logger.logError(exp)

    """
    Exevute jobs loop
    """
    def jobsLoop(self) -> None:
        self.__logger.log('Start jobs queue')
        while True:
            try:
                self.__queue.doJobs() # execute jobs from queue
            except Exception as exp:
                self.__logger.logError(exp)
