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

SHUTDOWNCOMMAND={'command' : 'shutdown'}
encryptionHandler = EncryptionHandler(b"Sixteen byte key")
offset = None

def startClockSync(currSocket):
    timeSend = time.time()
    messagedict = {"command" : "CS", "message" : str(timeSend)}
    print(str(timeSend) + '|' + str(time.time()))
    encrypted_msg = encryptionHandler.encrypt_msg(json.dumps(messagedict))
    currSocket.send(encrypted_msg)

    response = currSocket.recv(1024)
    timeRecv = time.time()
    response = response.decode('utf8')
    print(response)
    message = json.loads(response)['message'].split('|')
    
    print(f"t1:", {timeSend}, "t2:", \
        {message[0]}, "t3:", {message[1]}, "t4:", {timeRecv})
    t = [timeSend, float(message[0]), float(message[1]), timeRecv]
    
    roundTripTime = (t[3] - t[0]) - (t[2] - t[1])
    print("RTT:", {roundTripTime})
    
    clockOffset = ((t[2]-t[3]-roundTripTime/2) + (t[1] - t[0] - roundTripTime/2))/2
    messagedict = {"command" : "offset", "message" : str(clockOffset)}
    encrypted_msg = encryptionHandler.encrypt_msg(json.dumps(messagedict))
    currSocket.send(encrypted_msg)
    print("Clock offset:", {clockOffset})
    print("\n")

def sendTimeStamp(currSocket, timestamp: float):
    messagedict = {"command" : "evaluateMove", "message" : str(timestamp)}
    encrypted_msg = encryptionHandler.encrypt_msg(json.dumps(messagedict))
    currSocket.send(encrypted_msg)
    return

def run(host,port,dancerID):
    mySocket = socket.socket()
    mySocket.connect((host,port))
    print("Connection established with ", (host,port))
    mySocket.send(encryptionHandler.encrypt_msg(dancerID)) 

    command = encryptionHandler.decrypt_message(mySocket.recv(1024))
    while command != "quit":
        if command == "sync":
            for _ in range(10):
                print(f"Clock syncing for dancer:",{dancerID})
                startClockSync(mySocket)
                time.sleep(0.2)
            print("Sync complete for 10 rotations")

        if command == "start":            
            input("Press enter to send timestamp")
            timestamp = time.time()
            print("Spoofing timestamp for dancer " + str(dancerID) + ":" + str(timestamp))
            sendTimeStamp(mySocket, timestamp)
        command = encryptionHandler.decrypt_message(mySocket.recv(1024))

    print("Shutting down dancer number " + dancerID)
    encrypted_msg = encryptionHandler.encrypt_msg(json.dumps(SHUTDOWNCOMMAND))
    mySocket.send(encrypted_msg)
    mySocket.close()
    print("Quitting now")
    sys.exit()


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("Requires arguments:\n" + 
            "[type]: 'remote' for ssh to ultra96 or 'local' for localhost server testing\n" +
            "[dancerID]: string to uniquely identify dancer")
        sys.exit()

    if sys.argv[1] == "local":
        run('127.0.0.1', 10022, sys.argv[2])

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
            run('localhost', tunnel2.local_bind_port, sys.argv[2])          