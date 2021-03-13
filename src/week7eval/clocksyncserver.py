import socket
import sys
import json
import threading
import concurrent.futures
import time
from Util.encryption import EncryptionHandler

def variance(data, ddof=0):
    n = len(data)
    mean = sum(data) / n 
    return sum((x - mean) ** 2 for x in data) / (n - ddof)

class Ultra96Server:
    # Tuple containing "host" and "port" values for ultra96 server
    connection = ()

    # Holds socket address and port for each dancer, tied to dancer id as key
    clients = {}

    # Class for handling AES encryption
    encryptionhandler = None 

    # Holds last timestamps from the 3 dancers/laptops
    currTimeStamps = {}

    # Holds the last 10 recorded offsets from the 3 dancers
    # 2d array containing 10 lists of 3 offsets from each dancer 
    last10Offsets = {}

    # Used to iterate offset list from the back in order to update offsets
    currIndexClockOffset = {}

    # Holds average offsets for 3 dancers, calculated from last10Offsets
    currAvgOffsets = {}

    # Booleans to check if current moves have been received for each dancer
    currentMoveReceived = {}

    # Count to keep track of number of clock sync updates sent from each client
    # in current rotation (1-10)
    clocksyncCount = {}

    offsetLock = threading.Lock()
    timestampLock = threading.Lock()
    moveRcvLock = threading.Lock()

    # Initialize encryption handler and socket data + misc setup
    def __init__(self, host:str, port:int, key:bytes):
        self.connection = (host,port)
        self.encryptionhandler = EncryptionHandler(key.encode())

        # for _ in range(10):
        #     self.last10Offsets.append([None,None,None])
        return

    def updateTimeStamp(self, message : str, dancerID):
        print("Evaluating move...")
        print(f"time recorded by bluno:", {message})

        #calculate relative time using offset
        timestamp = float(message)
        relativeTS = timestamp - self.currAvgOffsets[dancerID]

        self.timestampLock.acquire()
        self.currTimeStamps[dancerID] = relativeTS
        self.timestampLock.release()

        return

    def broadcastMessage(self, message):
        message = self.encryptionhandler.encrypt_msg(message)
        for conn, addr in self.clients.values():
            print("BROADCAST: ",conn)
            conn.send(message)

    def respondClockSync(self, message : str, dancerID, timerecv):
        print(f"Received clock sync request from dancer, {dancerID}")
        timestamp = message
        print(f"t1 =",{timestamp})
        conn, addr = self.clients[dancerID]

        # response = str(timerecv) + "|" + str(time.time())
        response = json.dumps({'command' : 'CS', 'message': str(timerecv) + '|' + str(time.time())})
        conn.send(response.encode())

    # Must be called after acquiring offsetlock
    def updateAvgOffset(self):
        for dancerID, offsetList in self.last10Offsets.items():
            currSum = 0
            numOffsets = 10
            for offset in offsetList:
                if offset is None:
                    numOffsets -= 1
                    continue
                currSum += offset
            if numOffsets == 0:
                continue
            self.currAvgOffsets[dancerID] = currSum/numOffsets
        
    # Check if variance between 10 offsets in dancerID is too high.
    # If so, force another 10 updates with the specific dancerID
    def checkOffsetVar(self, dancerID):
        conn,addr = self.clients[dancerID]
        prevOffset = self.currAvgOffsets[dancerID]
        self.updateAvgOffset()

        clockDriftDetected = False
        offsetDiff = 0
        if not prevOffset is None:
            offsetDiff = abs(self.currAvgOffsets[dancerID] - prevOffset)
            clockDriftDetected = (offsetDiff > 5e-05)

        varLast10 = variance(self.last10Offsets[dancerID])
        print("VARIANCE FOR DANCER: ", dancerID, varLast10)
        if varLast10 > 1e-05 or clockDriftDetected:
            print("Offset variance too high: ",varLast10," or clock drift too high:",
                offsetDiff, "Resyncing for Dancer: ", dancerID)
            conn.send(self.encryptionhandler.encrypt_msg("sync"))
        
        return
            
    def updateOffset(self, message: str, dancerID):
        self.offsetLock.acquire()
        print(f"{dancerID} has received offsetlock")
        self.last10Offsets[dancerID][self.currIndexClockOffset[dancerID]] = float(message)
        self.currIndexClockOffset[dancerID] = (self.currIndexClockOffset[dancerID] - 1) % 10
        print(f"{dancerID} is releasing offsetlock")
        self.offsetLock.release()

        if self.clocksyncCount[dancerID] != 10:
            self.clocksyncCount[dancerID] += 1

        if self.clocksyncCount[dancerID] == 10:
            self.checkOffsetVar(dancerID)
            self.clocksyncCount[dancerID] = 0
            
        print("Updating dancer " + str(dancerID) + " offset to: " + message + "\n")
        return
    
    def calculateSyncDelay(self):
        sortedTimestamps = sorted(self.currTimeStamps.values())
        return (sortedTimestamps[2] - sortedTimestamps[0])

    def handleServerInput(self):
        command = input("The rest of this test script will be controlled via " +
            "server side input. Type 'sync' to perform clock synchronization " +
            "protocol and 'start' to broadcast start signal to all laptops/dancers\n")


        while command != "quit":
            if command == "sync":
                self.broadcastMessage("sync")
            if command == "start":
                self.broadcastMessage("start")
            command = input("Enter 'sync' to start clock sync and 'start' "+
                "to send start signal for move eval")
        self.broadcastMessage("quit")

    def handleClient(self, dancerID : str):
        conn,addr = self.clients[dancerID]
        try:
            while True:
                data = conn.recv(1024)
                timerecv = time.time()
                data = self.encryptionhandler.decrypt_message(data)
                data = json.loads(data)
                print("Received data:" + json.dumps(data) + "\n")
                # print(data.decode("utf8"))

                if data['command'] == "shutdown":
                    print(dancerID, ' Received shutdown signal\n')
                    break
                elif data['command'] == "CS":
                    self.respondClockSync(data['message'], dancerID, timerecv)
                elif data['command'] == "offset":
                    self.updateOffset(data['message'], dancerID)
                elif data['command'] == "evaluateMove":
                    self.updateTimeStamp(data['message'], dancerID)

                    self.moveRcvLock.acquire()
                    self.currentMoveReceived[dancerID] = True
                    if all(value == True for value in self.currentMoveReceived.values()):
                        print(f"Sync delay calculated:", {self.calculateSyncDelay()})
                        self.currentMoveReceived = {key: False for key in self.currentMoveReceived.keys()}
                    self.moveRcvLock.release()

                # decrypted_msg = encryptionHandler.decrypt_message(data)
            print(dancerID, " RETURNING\n")
        except:
            print("[ERROR][", dancerID, "] -> ", sys.exc_info())

    # Initialize connections with 3 dancers prior to start of evaluation
    def initializeConnections(self, numDancers = 3):
        mySocket = socket.socket()
        # host,port = self.connection
        mySocket.bind((self.connection))
        mySocket.listen(5)

        try:
            for _ in range(numDancers):
                conn,addr = mySocket.accept()
                data = self.encryptionhandler.decrypt_message(conn.recv(4096))
                print("Dancer ID: ", data)
                self.clients[data] = (conn,addr)
                print(addr, '\n')

                self.currIndexClockOffset[data] = 9 # initialize index counter to 9 for each dancer
                self.last10Offsets[data] = [None for _ in range(10)] # initialize last 10 offsets for dancer id to None
                self.currAvgOffsets[data] = None
                self.currentMoveReceived[data] = False
                self.clocksyncCount[data] = 0
            return 
        except:
            print(sys.exc_info()[0], "\n")
            return

if __name__ == "__main__":
    ultra96Server = Ultra96Server(host='127.0.0.1',port=10022,key="Sixteen byte key")
    ultra96Server.initializeConnections()

    # print("DANCER LIST: " + str(ultra96Server.clients))

    dancerIDlist = []
    for key in ultra96Server.clients:
        dancerIDlist.append(key)
    executor = concurrent.futures.ThreadPoolExecutor()
    # print(dancerIDlist)
    
    for dancer in dancerIDlist:
        executor.submit(ultra96Server.handleClient, dancer)
    executor.submit(ultra96Server.handleServerInput)

    executor.shutdown()
    print(f"offsets:", {str(ultra96Server.last10Offsets)})
    print(f"Last set of timestamps:", {str(ultra96Server.currTimeStamps)})