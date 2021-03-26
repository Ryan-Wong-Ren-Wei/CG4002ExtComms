from concurrent.futures.thread import ThreadPoolExecutor
from multiprocessing import Queue
import socket
import sys
import json
import threading
import concurrent.futures
import time
from types import DynamicClassAttribute
from Util.encryption import EncryptionHandler

NUM_DANCERS = 3

def variance(data, ddof=0):
    n = len(data)
    mean = sum(data) / n 
    return sum((x - mean) ** 2 for x in data) / (n - ddof)

# Class holding various data and functions for each dancer
class Dancer():
    def __init__(self, dancerID: int, conn :socket.socket):
        self.dancerID = dancerID
        self.conn = conn
        self.clockSyncResponseLock = threading.Event() # To handle client-server synchronization for clock sync protocol
        self.encryptionHandler = EncryptionHandler(b'Sixteen byte key')

        self.currIndexClockOffset = 9
        self.last10Offsets = [None for _ in range(10)]
        self.currAvgOffset = None
        self.clockSyncCount = 0 
        self.dataQueue = Queue()

    def handleClient(self, dataQueue):
        self.dataQueue = dataQueue
        conn = self.conn
        while True:
            try:
                receivedFromBuffer = self.recvall(conn)
                timerecv = time.time()
                packets = receivedFromBuffer.decode('utf8').split(",") # Split into b64encoded packets by ',' delimiter
                packets.pop(-1) # Pop last empty "packet"
                for packet in packets:
                    data = self.encryptionHandler.decrypt_message(packet)
                    if not data:
                        continue
                    data = json.loads(data)
                    # print("Received data:" + json.dumps(data) + "\n")
                    # print(data.decode("utf8"))
        
                    if data['command'] == "shutdown":
                        print(self.clockSyncResponseLockdancerID, ' Received shutdown signal\n')
                        break
                    elif data['command'] == "clocksync":
                        self.respondClockSync(data['message'], conn, timerecv, self.dancerID)
                    elif data['command'] == "offset":
                        self.updateOffset(data['message'])
                        self.clockSyncResponseLock.set()
                        
                    elif data['command'] == "timestamp":
                        pass
                        # self.moveCompletedFlag.clear()
                        # self.updateTimeStamp(data['message'], dancerID)
                        # self.currentMoveReceived[dancerID] = True
                        # if all(value == True for value in self.currentMoveReceived.values()):
                        #     print(f"Sync delay calculated:", {self.calculateSyncDelay()})
                        #     self.currentMoveReceived = {key: False for key in self.currentMoveReceived.keys()}
                    elif data['command'] == "data":
                        data.pop('command')
                        self.addData(data)
            except Exception as e:
                print("[ERROR][HANDLECLIENT]:", self.dancerID, e)
                return
    
    def addData(self, data):
        self.dataQueue.put(data)
        # with self.lockDataQueue:
        #     if not self.moveCompletedFlag.is_set():
        #         self.dancerDataDict[dancerID].put(data)
        #     else:
        #         while not self.dancerDataDict[dancerID].empty():
        #             self.dancerDataDict[dancerID].get()



    def recvall(self,conn: socket.socket):
        fullMessageReceived = False
        data = b''
        while not fullMessageReceived:
            data += conn.recv(1024)
            if data[-1] == 44: # 44 corresponds to ',' which is delimiter for end of b64 encoded msg
                fullMessageReceived = True
        return data

    def respondClockSync(self, message : str, conn: socket.socket, timerecv : float, dancerID):
        print(f"Received clock sync request from dancer, {dancerID}")
        timestamp = message
        print(f"t1 =",{timestamp})

        response = json.dumps({'command' : 'clocksync', 'message': str(timerecv) + '|' + str(time.time())})
        conn.send(self.encryptionHandler.encrypt_msg(response))

    def sendMessage(self, message : str):
        message = self.encryptionHandler.encrypt_msg(message)
        self.conn.send(message)
    
    def handleClockSync(self, doClockSync: threading.Event):
        while True:
            try:
                doClockSync.wait()
                for _ in range(10):
                    self.sendMessage('sync')
                    self.clockSyncResponseLock.clear()
                    self.clockSyncResponseLock.wait()
                doClockSync.clear()
            except Exception as e:
                print(e)
                return

    def updateOffset(self, message: str):
        self.last10Offsets[self.currIndexClockOffset] = float(message)
        self.currIndexClockOffset = (self.currIndexClockOffset - 1) % 10

        if self.clockSyncCount != 10:
            self.clockSyncCount += 1

        if self.clockSyncCount == 10:
            self.updateAvgOffset()
            self.clockSyncCount = 0
            
        print("Updating dancer " + str(self.dancerID) + " offset to: " + message + "\n")
        return

    def updateAvgOffset(self):
        offsetSum = 0
        numOffsets = 10
        for offset in self.last10Offsets:
            offsetSum += offset
        self.currAvgOffset = offsetSum/numOffsets


class Ultra96Server():
    def __init__(self, host:str, port:int, key:str):
        # each value in list holds dancer class
        self.addr = (host,port)
        self.dancers = [Dancer(0, None), Dancer(0, None), Dancer(0, None)]
        self.encryptionHandler = EncryptionHandler(key.encode('utf8'))
        self.globalShutDown = threading.Event()

    def initializeConnections(self, numDancers = NUM_DANCERS):
        socket96 = socket.socket()
        # host,port = self.connection
        socket96.bind((self.addr))
        socket96.listen(3)

        try:
            for _ in range(numDancers):
                conn,addr = socket96.accept()
                messageRecv = self.recvall(conn)
                dancerID = self.encryptionHandler.decrypt_message(messageRecv)
                print("Accepted connection from:", addr, "Dancer ID: ", dancerID)

                dancerID = int(dancerID)
                if dancerID not in [0,1,2]:
                    raise Exception("Dancer ID invalid, must be integer value 0,1 or 2") 
                self.dancers[dancerID] = Dancer(dancerID, conn)

        except Exception as e:
            print("[ERROR][initializeConnections]", e)

    def executeClientHandlers(self, executor, dataQueues):
        dancerID = 0
        for dancer in self.dancers:
            executor.submit(dancer.handleClient, dataQueues[dancerID])
            dancerID += 1
    
    def executeClockSyncHandlers(self, executor, doClockSync: threading.Event):
        for dancer in self.dancers:
            executor.submit(dancer.handleClockSync, doClockSync)

    def recvall(self,conn: socket.socket):
        fullMessageReceived = False
        data = b''
        while not fullMessageReceived:
            data += conn.recv(1024)
            if data[-1] == 44: # 44 corresponds to ',' which is delimiter for end of b64 encoded msg
                fullMessageReceived = True
        return data

    def broadcastMessage(self, message):
        print("BROADCASTING: ", message)
        message = self.encryptionHandler.encrypt_msg(message)
        for dancer in self.dancers:
            dancer.conn.send(message)


if __name__ == "__main__":
    server = Ultra96Server('127.0.0.1', 10022, 'Sixteen byte key')
    server.initializeConnections()