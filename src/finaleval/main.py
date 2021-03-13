from concurrent.futures import thread
from socket import setdefaulttimeout
import threading
from server import Ultra96Server
import concurrent.futures
import threading

class ControlMain():
    def __init__(self):
        self.ultra96Server = Ultra96Server(host='127.0.0.1', port=10022, key="Sixteen byte key")

    def run(self):
        dancerIDList = []
        self.ultra96Server.initializeConnections()
        for key in self.ultra96Server.clients:
            dancerIDList.append(key)
        executor = concurrent.futures.ThreadPoolExecutor()
        print(dancerIDList)
        
        for dancer in dancerIDList:
            print("HI")
            executor.submit(self.ultra96Server.handleClient, dancer)

        self.ultra96Server.broadcastMessage('sync')

        executor.shutdown()

if __name__ == "__main__":
    controlMain = ControlMain()
    controlMain.run()