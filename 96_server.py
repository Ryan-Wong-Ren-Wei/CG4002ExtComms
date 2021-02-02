import socket
from base64 import b64encode, b64decode
from getpass import getpass
from Util.encryption import EncryptionHandler
 
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