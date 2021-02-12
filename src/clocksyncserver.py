import socket
import sys
import json
import threading
import concurrent.futures
import time
from Util.encryption import EncryptionHandler

class Ultra96Server:
     # Set containing "host" and "port" values for ultra96 server
    connection = {}

    # Holds socket address and port for each dancer
    dancerList = None

    # Class for handling AES encryption
    encryptionhandler = None 

    # Holds last timestamps from the 3 dancers/laptops
    currTimeStamps = [0,0,0] 

    # Holds the last 10 recorded offsets from the 3 dancers
    # 2d array containing 10 lists of 3 offsets from each dancer 
    last10Offsets = [] 

    # Used to iterate offset list from the back in order to update offsets
    currIndexClockOffset = [9,9,9]

    # Holds average offsets for 3 dancers, calculated from last10Offsets
    currAvgOffsets = [None, None, None]

    # Booleans to check if current moves have been received for each dancer
    currentMoveReceived = [False,False,False] 

    offsetLock = threading.Lock()
    timestampLock = threading.Lock()
    moveRcvLock = threading.Lock()

    # Initialize encryption handler and socket data + misc setup
    def __init__(self, host, port, key):
        self.connection = {host,port}
        self.encryptionhandler = EncryptionHandler(key.encode())

        for _ in range(10):
            self.last10Offsets.append([None,None,None])
        return

    def updateTimeStamp(self, message : str, dancerID : int):
        print("Evaluating move...")
        print(f"time recorded by bluno:", {message})

        #calculate relative time using offset
        timestamp = float(message)
        relativeTS = timestamp - self.currAvgOffsets[dancerID - 1]

        self.timestampLock.acquire()
        self.currTimeStamps[dancerID - 1] = relativeTS
        self.timestampLock.release()

        return

    def respondClockSync(self, message : str, dancerID : int, timerecv):
        print(f"Received clock sync request from dancer, {dancerID}")
        timestamp = message
        print(f"t1 =",{timestamp})

        response = str(timerecv) + "|" + str(time.time())

        conn, addr = self.dancerList[dancerID]
        conn.send(response.encode())

    # Must be called after acquiring offsetlock
    def updateAvgOffsets(self):
        avgOffsets = [0,0,0]
        for offsets in self.last10Offsets:
            if offsets[0] is None or offsets[1] is None or offsets[2] is None:
                continue
            for currID in range(len(offsets)):
                avgOffsets[currID] += offsets[currID]
        
        self.currAvgOffsets = avgOffsets
        return avgOffsets
            
    def updateOffset(self, message: str, dancerID: int):
        self.offsetLock.acquire()
        print(f"{dancerID} has received offsetlock")
        self.last10Offsets[self.currIndexClockOffset[dancerID - 1]][dancerID - 1] = float(message)
        self.currIndexClockOffset[dancerID - 1] = (self.currIndexClockOffset[dancerID - 1] - 1) % 10
        self.updateAvgOffsets()
        print(f"{dancerID} is releasing offsetlock")
        self.offsetLock.release()

        print("Updating dancer " + str(dancerID) + " offset to: " + message)
        return
    
    def calculateSyncDelay(self):
        sortedTimestamps = sorted(self.currTimeStamps)
        return (sortedTimestamps[2] - sortedTimestamps[0])

    def handleClient(self, dancerID):
        conn,addr = self.dancerList[dancerID]
        try:
            print(f"Handling: \n {conn} \n {addr}")
            # print(conn,addr)
            while True:
                data = json.loads(conn.recv(1024).decode("utf8"))
                print("Received data:" + json.dumps(data))
                timerecv = time.time()
                # print(data.decode("utf8"))

                print(dancerID)
                if data['command'] == "shutdown":
                    print('Received shutdown signal')
                    break
                elif data['command'] == "CS":
                    self.respondClockSync(data['message'], dancerID, timerecv)
                elif data['command'] == "offset":
                    self.updateOffset(data['message'], dancerID)
                elif data['command'] == "evaluateMove":
                    self.updateTimeStamp(data['message'], dancerID)

                    self.moveRcvLock.acquire()
                    self.currentMoveReceived[dancerID] = True
                    if self.currentMoveReceived == [True for boolean in self.currentMoveReceived]:
                        print(f"Sync delay calculated:", {self.calculateSyncDelay()})
                    self.moveRcvLock.release()

                # decrypted_msg = encryptionHandler.decrypt_message(data)
            print("RETURNING")
        except:
            print(sys.exc_info())

    # Initialize connections with 3 dancers prior to start of evaluation
    def initializeConnections(self, numDancers = 3):
        tempDancerList = [] 
        mySocket = socket.socket()
        host,port = self.connection
        mySocket.bind((host,port))
        mySocket.listen(5)

        try:
            for _ in range(numDancers):
                conn,addr = mySocket.accept()
                tempDancerList.append((conn, addr))

            self.dancerList = tempDancerList
            return 
        except:
            print(sys.exc_info()[0])
            return
            # for conn, addr in tempDancerList:
            #     conn.close()

if __name__ == "__main__":
    ultra96Server = Ultra96Server(host='127.0.0.1',port=10022,key="Sixteen byte key")
    ultra96Server.initializeConnections()

    executor = concurrent.futures.ThreadPoolExecutor()


    for dancerID in range(len(ultra96Server.dancerList)):
        executor.submit(ultra96Server.handleClient, dancerID)

    executor.shutdown()

    print(f"offsets:", {str(ultra96Server.last10Offsets)})
    print(f"Last set of timestamps:", {ultra96Server.currTimeStamps})
    for conn, addr in ultra96Server.dancerList:
        conn.close()