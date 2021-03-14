import time 
import sys
from multiprocessing import Event
import getpass
from sshtunnel import SSHTunnelForwarder
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad
from Cryptodome.Random import get_random_bytes
from base64 import b64encode
import json
import random
import socket
import queue
from Util.encryption import EncryptionHandler

SHUTDOWNCOMMAND = {'command' : 'shutdown'}
class LaptopClient():
    def __init__(self, host, port, dancerID):
        self.moveStarted = Event()
        self.evalStarted = Event()
        self.host = host
        self.port = port
        self.encryptionHandler = EncryptionHandler(b'Sixteen byte key')
        self.dancerID = dancerID

    def sendMessage(self, message):
        encrypted_message = self.encryptionHandler.encrypt_msg(message)
        self.mySocket.send(encrypted_message)

    def handleBlunoData(self, inputQueue):
        try:
            packet = None
            while True:
                packet = None 
                packet = inputQueue.get()
                if packet is not None:
                    if not self.evalStarted.is_set():
                        print("Eval not yet started, ignoring data")
                        print(packet)
                        continue
                    if packet['moveFlag'] == 1:
                        if not self.moveStarted.is_set():
                            # if move hasn't started, set flag and send timestamp
                            self.moveStarted.set()
                            self.sendMessage(json.dumps({"command" : "timestamp", "message" : time.time()}))
                        packet['command'] = 'data'
                        self.sendMessage(json.dumps(packet))
                        print(packet)
                    else:
                        self.moveStarted.clear()
                else:
                    print("No packet found...")
        except:
            print("HANDLEBLUNO", sys.exc_info)
#            time.sleep(0.1)

    def startClockSync(self):
        timeSend = time.time()
        messagedict = {"command" : "clocksync", "message" : str(timeSend)}
        print(str(timeSend) + '|' + str(time.time()))
        encrypted_msg = self.encryptionHandler.encrypt_msg(json.dumps(messagedict))
        self.mySocket.send(encrypted_msg)

        response = self.mySocket.recv(1024)
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
        encrypted_msg = self.encryptionHandler.encrypt_msg(json.dumps(messagedict))
        self.mySocket.send(encrypted_msg)
        print("Clock offset:", {clockOffset})
        print("\n")

    def handleServerCommands(self):
        command = self.mySocket.recv(4096)
        command = self.encryptionHandler.decrypt_message(command)
        while command != "quit":
            if command == "sync":
                self.startClockSync()
            elif command == "start":
                self.evalStarted.set()  
            command = self.mySocket.recv(4096)
            command = self.encryptionHandler.decrypt_message(command)
        print("Shutting down dancer number " + self.dancerID)
        encrypted_msg = self.encryptionHandler.encrypt_msg(json.dumps(SHUTDOWNCOMMAND))
        self.mySocket.send(encrypted_msg)
        self.mySocket.close()
        print("Quitting now")
        sys.exit()

    def connectAndIdentify(self, host, port, dancerID=random.randint(0,10)):
        self.mySocket = socket.socket()
        self.mySocket.connect((host,port))
        print(dancerID, ": Connection established with ", (host,port))
        msg = self.encryptionHandler.encrypt_msg(dancerID)
        self.mySocket.send(msg)

    def start(self, remote = False):
        if remote:
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
                    self.connectAndIdentify('localhost', tunnel2.local_bind_port, sys.argv[2])
        else:
            self.connectAndIdentify('127.0.0.1', 10022, self.dancerID)

if __name__ == "__main__":
    client = LaptopClient("127.0.0.1", 10022)
    client.start()
    inputQueue = queue.Queue()
    for _ in range(50):
        dummy_packet = None
        dummy_packet = {
                    "GyroX": random.randint(-40000, 40000),
                    "GyroY": random.randint(-40000, 40000),
                    "GyroZ": random.randint(-40000, 40000),
                    "AccelX": random.randint(-40000, 40000),
                    "AccelY": random.randint(-40000, 40000),
                    "AccelZ": random.randint(-40000, 40000),
                    "StartFlag": 1
                }
        
        inputQueue.put(dummy_packet)
    client.handleBlunoData(inputQueue)
