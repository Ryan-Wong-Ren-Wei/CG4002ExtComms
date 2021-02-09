import time 
import sys
from threading import local
import getpass
from sshtunnel import SSHTunnelForwarder
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad
from Cryptodome.Random import get_random_bytes
from base64 import b64encode
import json
import socket
from Util.encryption import EncryptionHandler


def startClockSync(currSocket):
    timeSend = time.time()
    currSocket.send(("@CS" + str(timeSend)).encode("utf8"))

    response = currSocket.recv(1024).decode('utf8')
    response = response.split("|")
    timeRecv = time.time()

    print(f"t1:", {timeSend}, "t2:", \
        {response[0]}, "t3:", {response[1]}, "t4:", {timeRecv})
    t = [timeSend, float(response[0]), float(response[1]), timeRecv]
    
    roundTripTime = (t[3] - t[0]) - (t[2] - t[1])
    print("RTT:", {roundTripTime})
    
    clockOffset = ((t[1] - t[0]) + (t[2] - t[3]))/2 
    print("Clock offset:", {clockOffset})
    print("\n")

def connectTo96(host,port):
    key = 'Sixteen byte key'
    socketList = []
    for _ in range(3):
        mySocket =  socket.socket()
        mySocket.connect((host,port))   
        socketList.append(mySocket)

    command = input("type quit to quit -> ")
    while command != "quit":
        dancerID = 0
        for currSocket in socketList:
            print(f"Clock syncing for dancer:",{dancerID})
            startClockSync(currSocket)
            dancerID += 1
        # time.sleep(30)
        command = input("type quit to quit -> ")

    x = 0
    for currSocket in socketList:
        print("Shutting down dancer number " + str(x))
        currSocket.send(b"shutdown")
        currSocket.close()
        x += 1
    print("Quitting now")
    sys.exit()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "local":
        connectTo96('127.0.0.1', 10022)

    REMOTE_SERVER_IP = 'sunfire.comp.nus.edu.sg'
    PRIVATE_SERVER_IP = '137.132.86.228'

    username = input("Enter ssh username: ")
    password =  getpass.getpass("Enter ssh password: ")
    key = 'Sixteen byte key' #remember to hide
    with SSHTunnelForwarder(
        REMOTE_SERVER_IP,
        ssh_username=username,
        ssh_password=password,
        remote_bind_address=(PRIVATE_SERVER_IP, 22),
        local_bind_address=('localhost', 10022)
    ) as tunnel1:
        print('Tunnel opened to sunfire.comp.nus.edu.sg with...')
        print('Address: ' + str(tunnel1.local_bind_address))
        print('Port no: ' + str(tunnel1.local_bind_port))
        with SSHTunnelForwarder(
            ('localhost', 10022),
            ssh_username='xilinx',
            ssh_password='xilinx',
            remote_bind_address=('localhost', 10022)
        ) as tunnel2:
            print('Tunnel opened to ultra96 board with...')
            print('Address: ' + str(tunnel2.local_bind_address))
            print('Port no: ' + str(tunnel2.local_bind_port))  
            connectTo96('localhost', tunnel2.local_bind_port)          