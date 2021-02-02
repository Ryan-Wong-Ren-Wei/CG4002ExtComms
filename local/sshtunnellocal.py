from threading import local
import getpass
import socket
from sshtunnel import SSHTunnelForwarder
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad
from Cryptodome.Random import get_random_bytes
from base64 import b64encode
import json
from encryption import EncryptionHandler

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
        remote_bind_address=('localhost', 10022),
        local_bind_address=('localhost', 8080)
    ) as tunnel2:
        print('Tunnel opened to ultra96 board with...')
        print('Address: ' + str(tunnel2.local_bind_address))
        print('Port no: ' + str(tunnel2.local_bind_port))
        host = '127.0.0.1'
        port = 8080
         
        mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        mySocket.connect((host,port))
         
        message = input(" -> ")
         
        while message != 'q':
            encryptionHandler = EncryptionHandler(key.encode())
            encrypted_msg = encryptionHandler.encrypt_msg
            mySocket.send(encrypted_msg)
            data = mySocket.recv(1024).decode()
                
            print ('Received from server: ' + data)
                
            message = input(" -> ")
                 
        mySocket.close()
    

print('FINISH!')