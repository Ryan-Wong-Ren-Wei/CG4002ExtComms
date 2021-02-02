# CLIENT SIDE FOR ULTRA 96 

import socket
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad
from Cryptodome.Random import get_random_bytes
from base64 import b64encode
import json

def Main():
    key = b'Sixteen byte key' # Remember to hide or use input for this

    host = '127.0.0.1'
    port = 10022
    
    mySocket = socket.socket()
    mySocket.connect((host,port))
        
       
    quit = False
    while not quit:
        message = input(" -> ") 
        if message == 'q':
            message = '# |logout| ' #set action to logout if quit
            quit = True
        cipher = AES.new(key, AES.MODE_CBC)
        message += ' ' * (16 - len(message) % 16)
        ct_bytes = cipher.encrypt(message.encode())
        print(AES.block_size)
        iv = cipher.iv
        ct = ct_bytes
        # json_bytes = json.dumps({'iv': iv, 'ciphertext': ct}).encode()
        encryptedMessage = b64encode(cipher.iv + ct_bytes)
        print(encryptedMessage)
        mySocket.send(encryptedMessage)
        data = mySocket.recv(1024).decode()
            
        print ('Received from server: ' + data)
                
    mySocket.close()
 
if __name__ == '__main__':
    Main()