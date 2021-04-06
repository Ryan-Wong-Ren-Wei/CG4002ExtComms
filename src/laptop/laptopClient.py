import time 
import sys
from multiprocessing import Event, Lock
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
import sshtunnel

SHUTDOWNCOMMAND = {'command' : 'shutdown'}
class LaptopClient():
    def __init__(self, host, port, dancerID):
        self.moveStarted = Event()
        self.evalStarted = Event()
        self.socketLock = Lock()
        self.host = host
        self.port = port
        self.encryptionHandler = EncryptionHandler(b'Sixteen byte key')
        self.dancerID = dancerID

    def sendMessage(self, message):
        print("SENDING: ", message)
        encrypted_message = self.encryptionHandler.encrypt_msg(message) + b',' #Send b64encoded bytes with ',' delimiter as ',' is not valid b64encoded char
        self.mySocket.send(encrypted_message)

    def handleBlunoData(self, inputQueue):
        try:
            packet = None
            while True:
                packet = None 
                packet = inputQueue.get()
                if packet is not None:
                    if not self.evalStarted.is_set():
                        # print("Eval not yet started, ignoring data")
                        # print(packet)
                        continue
                    if packet['PosChangeFlag'] != 0:
                        self.sendMessage(json.dumps({"command" : "poschange", "message" : packet['PosChangeFlag']}))
                    if packet['moveFlag'] == 1:
                        if not self.moveStarted.is_set():
                            # if move hasn't started, set flag and send timestamp
                            self.moveStarted.set()
                            self.sendMessage(json.dumps({"command" : "timestamp", "message" : packet['time']}))
                        packet['command'] = 'data'
                        self.sendMessage(json.dumps(packet))
                        # print(packet)
                else:
                    print("No packet found...")
                time.sleep(0.04)
        except Exception as e:
            print("HANDLEBLUNO:", e)
            sys.exit()
            

    def startClockSync(self):
        self.timeSend = time.time()
        messagedict = {"command" : "clocksync", "message" : str(self.timeSend)}
        print("SENDING", messagedict)
        self.sendMessage(json.dumps(messagedict))

    def respondClockSync(self, timestamps, timeRecv):
        timestamps = json.loads(timestamps)['message'].split('|')
        print(f"t1:", {self.timeSend}, "t2:", \
            {timestamps[0]}, "t3:", {timestamps[1]}, "t4:", {timeRecv})
        t = [self.timeSend, float(timestamps[0]), float(timestamps[1]), timeRecv]
        
        roundTripTime = (t[3] - t[0]) - (t[2] - t[1])
        print("RTT:", {roundTripTime})
        
        clockOffset = ((t[2]-t[3]-roundTripTime/2) + (t[1] - t[0] - roundTripTime/2))/2
        messagedict = {"command" : "offset", "message" : str(clockOffset)}
        self.sendMessage(json.dumps(messagedict))
        print("Clock offset:", {clockOffset})
        print("\n")
        
    def handleServerCommands(self): 
        command = self.mySocket.recv(4096)
        timeRecv = time.time()
        command = self.encryptionHandler.decrypt_message(command)
        print("COMMAND RECEIVED:", command)
        while command != "quit":
            if command == "sync":
                self.startClockSync()
            elif command == "start":
                self.evalStarted.set()
            elif command == 'moveComplete':
                self.moveStarted.clear() 
            elif "clocksync" in command:
                self.respondClockSync(command,timeRecv)

            command = self.mySocket.recv(4096)
            timeRecv = time.time()
            command = self.encryptionHandler.decrypt_message(command)
            print("COMMAND RECEIVED:", command)
        print("Shutting down dancer number " + self.dancerID)
        self.sendMessage(json.dumps(SHUTDOWNCOMMAND))
        self.mySocket.close()
        print("Quitting now")
        sys.exit()

    def connectAndIdentify(self, host, port, dancerID):
        self.mySocket = socket.socket()
        self.mySocket.connect((host,port))
        print(dancerID, ": Connection established with ", (host,port))
        self.sendMessage(dancerID)

    def start(self, remote = False):
        if remote:
            REMOTE_SERVER_IP = 'sunfire.comp.nus.edu.sg'
            PRIVATE_SERVER_IP = '137.132.86.228'

            username = input("Enter ssh username: ")
            password =  getpass.getpass("Enter ssh password: ")
            key = 'Sixteen byte key' #remember to hide
            tunnel1 = sshtunnel.open_tunnel(
                (REMOTE_SERVER_IP, 22), 
                remote_bind_address=(PRIVATE_SERVER_IP, 22),
                ssh_username=username,
                ssh_password=password,
                # local_bind_address=('127.0.0.1', 8081),
                block_on_close=False
            )
            tunnel1.start()
            print('[Tunnel Opened] Tunnel into Sunfire opened ' +
                str(tunnel1.local_bind_port))
            tunnel2 = sshtunnel.open_tunnel(
                ssh_address_or_host=(
                    'localhost', tunnel1.local_bind_port),  # ssh into xilinx
                remote_bind_address=('127.0.0.1', 10022),  # binds xilinx host
                ssh_username='xilinx',
                ssh_password='xilinx',
                local_bind_address=('127.0.0.1', 10022),  # localhost to bind it to
                block_on_close=False
            )
            tunnel2.start()
            self.connectAndIdentify('127.0.0.1', 10022, self.dancerID)
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
