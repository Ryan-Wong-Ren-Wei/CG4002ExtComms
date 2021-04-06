from concurrent.futures import thread
from socket import setdefaulttimeout
import threading
from server import NUM_DANCERS, Ultra96Server
import concurrent.futures
import threading
from evalClient import EvalClient
from queue import Queue
import time
from ML import handleML
import sys

class ControlMain():
    def __init__(self):
        self.doClockSync = threading.Event()
        self.doClockSync.set()
        self.globalShutDown = threading.Event()
        self.evalClient = EvalClient('137.132.92.127', 8888, controlMain=self)
        self.moveCompletedFlag = threading.Event()
        self.currPrediction = None
        self.dataQueues = [Queue() for _ in range(NUM_DANCERS)]
        self.dataQueueLock = threading.Event()
        self.outputForEval = {"positions": None, "action" : None, "delay" : None}
        self.rdyForEval = threading.Event()

        # Logic list of current dancer positions
        self.dancerPositions = [1,2,3]

        # Logic list of position change data received from laptop
        self.positionChange = [0,0,0]
        pass
        
    def run(self):
        self.server = Ultra96Server('127.0.0.1', 10022, 'Sixteen byte key')
        try:
            self.server.initializeConnections()
        except Exception as e:
            print(e)
        
        executor = concurrent.futures.ThreadPoolExecutor()

        self.server.executeClientHandlers(executor, self.dataQueues, self.dataQueueLock, self.positionChange)
        time.sleep(3)

        self.server.executeClockSyncHandlers(executor, self.doClockSync)
        time.sleep(3)
        
        input("Press Enter to connect to eval server")
        self.evalClient.connectToEval()
        time.sleep(60) 
        executor.submit(handleML, self.dataQueues, self.outputForEval, self.globalShutDown, self.rdyForEval, self.dataQueueLock)
        executor.submit(self.evalClient.handleEval, self.outputForEval, self.rdyForEval, self.server, self.globalShutDown,
            self.dancerPositions, self.positionChange, self.doClockSync)
        self.server.broadcastMessage('start')


        complete = False
        while not complete:
            try:
                time.sleep(10)
            except KeyboardInterrupt:
                print("Exiting.")
                self.server.broadcastMessage('quit')
                self.evalClient.sendToEval(quit=True)
                complete = True
                executor.shutdown(wait=False,cancel_futures=True)
                self.globalShutDown.set()


if __name__ == "__main__":
    controlMain = ControlMain()
    controlMain.run()
