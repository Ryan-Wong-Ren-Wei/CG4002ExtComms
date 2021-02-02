import socket
from Util.encryption import EncryptionHandler
from base64 import b64encode, b64decode

host = '127.0.0.1'
port = 10022
key = 'Sixteen byte key'
    
mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mySocket.connect((host,port))
    
message = input(" -> ")
    
while message != 'q':
    encryptionHandler = EncryptionHandler(key.encode('utf8'))
    encrypted_msg = encryptionHandler.encrypt_msg(message)
    mySocket.send(encrypted_msg)
    data = mySocket.recv(1024).decode()
        
    print ('Received from server: ' + data)
        
    message = input(" -> ")
            
mySocket.close()