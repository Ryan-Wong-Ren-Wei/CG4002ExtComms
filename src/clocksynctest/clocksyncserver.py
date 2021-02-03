import socket
import sys
import json
import threading
import concurrent.futures

class Ultra96Server:
    dancerList = None
    messageList = []

    def __init__(self):
        return

    def handleClient(self, conn, addr):
        print("hello")
        try:
            print(f"Handling: \n {conn} \n {addr}")
            # print(conn,addr)
            while True:
                data = conn.recv(1024)
                # print(data.decode("utf8"))
                if not data:
                    print('no data')
                    break
                # decrypted_msg = encryptionHandler.decrypt_message(data)
                print(f"Message received: ", {data.decode('utf8')})
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
            for conn,addr in self.dancerList:
                print(conn)
                print(addr)
            return 
        except:
            print(sys.exc_info()[0])
            return
            # for conn, addr in tempDancerList:
            #     conn.close()

def handleClient(self, conn, addr):
    print("hello")
    try:
        print(f"Handling: \n {conn} \n {addr}")
        # print(conn,addr)
        while True:
            data = conn.recv(1024)
            # print(data.decode("utf8"))
            if not data:
                print('no data')
                break
            # decrypted_msg = encryptionHandler.decrypt_message(data)
            print(f"Message received: ", {data.decode('utf8')})
            conn.send("Received msg, awaiting next msg".encode())
        print("RETURNING")
    except:
        print(sys.exc_info())

ultra96Server = Ultra96Server()
ultra96Server.initializeConnections('127.0.0.1', 10022)

# executor = concurrent.futures.ThreadPoolExecutor()


with concurrent.futures.ThreadPoolExecutor() as executor:
    for conn, addr in ultra96Server.dancerList:
        executor.submit(ultra96Server.handleClient, conn,addr)
    # conn,addr = ultra96Server.dancerList[0]
    # executor.submit(handleClient, conn, addr)

executor.shutdown()
# for conn, addr in ultra96Server.dancerList:
#     conn.close()

# executor.shutdown(wait=True)

# for conn,addr in ultra96Server.dancerList:
#     conn.close()

# input("Press any key and Enter to close -> ")

# print(ultra96Server.messageList)

