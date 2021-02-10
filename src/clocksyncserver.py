import socket
import sys
import json
import threading
import concurrent.futures
import time

class Ultra96Server:
    dancerList = None
    currTimeStamps = [0,0,0]
    clockOffsets = [0,0,0]

    offsetLock = threading.Lock()

    def __init__(self):
        return

    def updateTimeStamp(self, message : str, dancerID : int):
        print("Evaluating move...")
        print(f"time recorded by bluno:", {message})

        #calculate relative time using offset
        timestamp = float(message)
        relativeTS = timestamp - self.clockOffsets[dancerID - 1]
        self.currTimeStamps[dancerID - 1] = relativeTS
        return

    def respondClockSync(self, message : str, dancerID : int, timerecv):
        print(f"Received clock sync request from dancer, {dancerID}")
        timestamp = message
        print(f"t1 =",{timestamp})

        response = str(timerecv) + "|" + str(time.time())

        conn,addr = self.dancerList[dancerID]
        conn.send(response.encode())
        
    def updateOffset(self, message: str, dancerID: int):
        while(self.offsetLock.locked()):
            continue

        self.offsetLock.acquire()
        self.clockOffsets[dancerID - 1] = float(message)
        self.offsetLock.release()
        print("Updating dancer " + str(dancerID) + " offset to: " + message)
        return

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
                    
                # decrypted_msg = encryptionHandler.decrypt_message(data)
            print("RETURNING")
        except:
            print(sys.exc_info())

    def initializeConnections(self, host : str, port : int, numDancers = 3):
        print(host,port)
        tempDancerList = [] 
        mySocket = socket.socket()
        mySocket.bind((host,port))
        mySocket.listen(5)

        try:
            for dancerID in range(numDancers):
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
    ultra96Server = Ultra96Server()
    ultra96Server.initializeConnections('127.0.0.1', 10022)

    executor = concurrent.futures.ThreadPoolExecutor()


    for dancerID in range(len(ultra96Server.dancerList)):
        executor.submit(ultra96Server.handleClient, dancerID)

    executor.shutdown()

    print(f"offsets:", {str(ultra96Server.clockOffsets)})
    timestamps = sorted(ultra96Server.currTimeStamps)
    print(f"timestamps recorded:" , {str(timestamps)})
    print(f"Sync delay:", {timestamps[2] - timestamps[0]})
    for conn, addr in ultra96Server.dancerList:
        conn.close()