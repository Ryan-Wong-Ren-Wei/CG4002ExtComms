import socket
import time 
import sys

def startClockSync(socket):
    timeSend = time.time()
    socket.send(("@CS" + str(timeSend)).encode("utf8"))

    response = socket.recv(1024).decode('utf8')
    response = response.split("|")
    timerecv = time.time()

    RTT = (float(response[0]) - timeSend) - \
        (float(response[1]) - timerecv)
    print(RTT)
    print(response)


host = '127.0.0.1'
port = 10022
key = 'Sixteen byte key'
    
socketList = []
for _ in range(3):
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mySocket.connect((host,port))   
    socketList.append(mySocket)

# handleClockSync(socketList)
command = input("type quit to quit -> ")
while command != "quit":
    for socket in socketList:
        startClockSync(socket)
    # time.sleep(30)
    command = input("type quit to quit -> ")

for socket in socketList:
    socket.send(b"shutdown")
    socket.close()
print("Quitting now")