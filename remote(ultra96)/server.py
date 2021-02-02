import socket
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
from Cryptodome.Random import get_random_bytes
from base64 import b64encode, b64decode
from getpass import getpass
from encryption import EncryptionHandler
import json
 
def startServer(host : str, port : int):
    mySocket = socket.socket()
    mySocket.bind((host,port))
     
    mySocket.listen(1)
    conn, addr = mySocket.accept()
    print ("Connection from: " + str(addr))
    return conn, addr

def Main():
    # key = getpass("enter key: ")
    key = 'Sixteen byte key'
    encryptionHandler = EncryptionHandler(key.encode())
    host = "127.0.0.1"
    port = 10022
    
    conn, addr = startServer(host, port)
    
    while True:
        data = conn.recv(1024)
        print(data.decode("utf8"))
        if not data:
            break
        decrypted_msg = encryptionHandler.decrypt_message(data)
        print(f"Message received: ", {decrypted_msg})
        conn.send("Received msg, awaiting next msg".encode())

    print("Closing connection")
    conn.close()
     
if __name__ == '__main__':
    Main()