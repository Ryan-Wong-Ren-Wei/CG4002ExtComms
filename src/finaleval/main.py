from concurrent.futures import thread
from socket import setdefaulttimeout
import threading
from server import Ultra96Server
import concurrent.futures
import threading
from evalClient import EvalClient
from queue import Queue
import time
from ML import eatQ

class ControlMain():
    def __init__(self):
        self.lockDataQueue = threading.Lock()
        self.dancerDataDict = {}

        #if true, then broadcast clock sync. If false, wait for move eval then set to true
        self.doClockSync = threading.Event()
        self.doClockSync.set()

        self.ultra96Server = Ultra96Server(host='127.0.0.1', port=10022, key="Sixteen byte key", controlMain=self)
        self.evalClient = EvalClient('127.0.0.1', 10023, controlMain=self)
        
    def run(self):
        dancerIDList = []
        self.ultra96Server.initializeConnections()
        for key in self.ultra96Server.clients:
            dancerIDList.append(key)
        executor = concurrent.futures.ThreadPoolExecutor()
        print(dancerIDList)
        
        for dancer in dancerIDList:
            executor.submit(self.ultra96Server.handleClient, dancer)
        # executor.submit(self.ultra96Server.handleClockSync)
        
        for _ in range(10):
            self.ultra96Server.broadcastMessage('sync')
            time.sleep(0.4)

        input("Press Enter to connect to eval server")
        try:
            # self.evalClient.connectToEval()
            self.ultra96Server.broadcastMessage('start')
            executor.submit(eatQ, self.dancerDataDict["shittyprogrammer"])
            # Start ML thingy here
        except:
            pass

        executor.shutdown()

        for key,value in self.dancerDataDict.items():
            while not value.empty():
                print(value.get())
        print(self.dancerDataDict)

if __name__ == "__main__":
    controlMain = ControlMain()
    controlMain.run()