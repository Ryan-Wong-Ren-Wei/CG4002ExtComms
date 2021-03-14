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
import random
import socket
import queue
from Util.encryption import EncryptionHandler

class LaptopClient():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.encryptionHandler = EncryptionHandler(b'Sixteen byte key')

    def sendMessage(self, message):
        encrypted_message = self.encryptionHandler.encrypt_msg(message)
        self.mySocket.send(encrypted_message)

    def handleBlunoData(self, inputQueue: queue.Queue):
        packet = None
        while not inputQueue.empty():
            packet = None 
            packet = inputQueue.get()
    
            if packet is not None:
                self.sendMessage(json.dumps(packet))
                print(packet)
            else:
                print("No packet found...")
            time.sleep(0.1)
            

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
            self.connectAndIdentify('127.0.0.1', 10022, sys.argv[2])

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