# CLIENT SIDE FOR ULTRA 96 

import socket
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad
from Cryptodome.Random import get_random_bytes
from base64 import b64encode
import json
import time


POSITIONS = ['1 2 3', '3 2 1', '2 3 1', '3 1 2', '1 3 2', '2 1 3']       
ACTIONS = ['gun', 'sidepump', 'hair'] 

def Main():
    key = b'Sixteen byte key' # Remember to hide or use input for this

    host = '127.0.0.1'
    port = 10022
    
    mySocket = socket.socket()
    mySocket.connect((host,port))
       
    quit = False
    x = 0

    # data = mySocket.recv(1024).decode()
    # print(data)

    while not quit:
        command = input(" -> ") 
        if command == 'q':
            message = '# |logout| ' #set action to logout if quit
            quit = True
        else:
            message = '#' + POSITIONS[x%6] + '|' + ACTIONS[x%3] + '|' + '0.005'
        cipher = AES.new(key, AES.MODE_CBC)
        message += ' ' * (16 - len(message) % 16)
        print(message)
        ct_bytes = cipher.encrypt(message.encode())
        print(AES.block_size)
        iv = cipher.iv
        ct = ct_bytes
        encrypted_msg = b64encode(cipher.iv + ct_bytes)
        print(encrypted_msg)
        mySocket.send(encrypted_msg)
        data = mySocket.recv(1024).decode()
            
        print ('Received from server: ' + data)
        x += 1
                
    mySocket.close()
 
if __name__ == '__main__':
    Main()