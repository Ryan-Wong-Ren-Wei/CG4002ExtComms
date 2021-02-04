import socket
import sys
import json
import threading
import concurrent.futures
import time

class Ultra96Server:
    dancerList = None
    messageList = []

    def __init__(self):
        return

    def parseClockSync(self, data : str, dancerID : int, timerecv):
        print(f"Received clock sync request from dancer, {dancerID}")
        timestamp = data[3:]
        print(f"t1 =",{timestamp})

        response = str(timerecv) + "|" + str(time.time())

        conn,addr = self.dancerList[dancerID]
        conn.send(response.encode())
        

    def handleClient(self, dancerID):
        conn,addr = self.dancerList[dancerID]
        try:
            print(f"Handling: \n {conn} \n {addr}")
            # print(conn,addr)
            while True:
                data = conn.recv(1024).decode("utf8")
                timerecv = time.time()
                # print(data.decode("utf8"))
                if data == "shutdown":
                    print('Received shutdown signal')
                    break
                elif data[0:3] == "@CS":
                    self.parseClockSync(data, dancerID, timerecv)
                    
                # decrypted_msg = encryptionHandler.decrypt_message(data)
                else:    
                    print(f"Message received:", {data}, "from dancer:", {dancerID})
                    conn.send("Received msg, awaiting next msg".encode())
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

ultra96Server = Ultra96Server()
ultra96Server.initializeConnections('127.0.0.1', 10022)

executor = concurrent.futures.ThreadPoolExecutor()

for dancerID in range(len(ultra96Server.dancerList)):
    executor.submit(ultra96Server.handleClient, dancerID)

executor.shutdown()
for conn, addr in ultra96Server.dancerList:
    conn.close()