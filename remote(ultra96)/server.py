import socket
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
from Cryptodome.Random import get_random_bytes
from base64 import b64encode, b64decode
import json
 
def Main():
    key = b'Sixteen byte key' # Remember to hide or use input for this
    host = "127.0.0.1"
    port = 10022
     
    mySocket = socket.socket()
    mySocket.bind((host,port))
     
    mySocket.listen(1)
    conn, addr = mySocket.accept()
    print ("Connection from: " + str(addr))
    
    while True:
        data = conn.recv(1024).decode()
        if not data:
            break
        b64 = json.loads(data)
        iv = b64decode(b64['iv'])
        ct = b64decode(b64['ciphertext'])
        
        cipher = AES.new(key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        print("The message was: ", pt)
        
        data = str(data).upper()
        print ("sending: " + str(data))
        conn.send(data.encode())

    conn.close()
     
if __name__ == '__main__':
    Main()