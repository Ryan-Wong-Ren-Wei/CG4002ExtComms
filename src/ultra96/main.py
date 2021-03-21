from concurrent.futures import thread
from socket import setdefaulttimeout
import threading
from server import Ultra96Server
import concurrent.futures
import threading
from evalClient import EvalClient
from queue import Queue
import time
from dummyML import handleML
import sys

class ControlMain():
    def __init__(self):
        self.lockDataQueue = threading.Lock()
        self.dancerDataDict = {}
        self.output = None
        self.moveCompletedFlag = threading.Event()
        self.globalShutDown = threading.Event()

        #if true, then broadcast clock sync. If false, wait for move eval then set to true
        self.doClockSync = threading.Event()
        self.doClockSync.set()

        self.ultra96Server = Ultra96Server(host='127.0.0.1', port=10022, key="Sixteen byte key", controlMain=self)
        self.evalClient = EvalClient('127.0.0.1', 8888, controlMain=self)
        
    def run(self):
        dancerIDList = []
        try:
            self.ultra96Server.initializeConnections()
        except Exception as e:
            print("Error initializing connections: ", e)
        for key in self.ultra96Server.clients:
            dancerIDList.append(key)
        executor = concurrent.futures.ThreadPoolExecutor()
        print(dancerIDList)
        
        for dancer in dancerIDList:
            executor.submit(self.ultra96Server.handleClient, dancer)
        
        for _ in range(10):
            self.ultra96Server.broadcastMessage('sync')
            time.sleep(0.4)

        input("Press Enter to connect to eval server")
        try:
            self.evalClient.connectToEval()
            # time.sleep(60)
            print("60 seconds time out done, starting evaluation")
            self.ultra96Server.broadcastMessage('start')
            for dancerID in dancerIDList:
                executor.submit(handleML, self.dancerDataDict[dancerID], self.output, self.moveCompletedFlag, self.evalClient, self.globalShutDown)
            # Start ML thingy here
        except Exception as e:
            print("Exception, ", e, "Exiting.")
            self.ultra96Server.broadcastMessage('quit')
            self.evalClient.sendToEval(quit=True)
            sys.exit()

        complete = False
        while not complete:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                print("Exiting.")
                self.ultra96Server.broadcastMessage('quit')
                self.evalClient.sendToEval(quit=True)
                complete = True
                executor.shutdown(wait=False,cancel_futures=True)
                self.globalShutDown.set()

        # executor.shutdown()

        for key,value in self.dancerDataDict.items():
            while not value.empty():
                print(value.get())
        print(self.dancerDataDict)

if __name__ == "__main__":
    controlMain = ControlMain()
    controlMain.run()
