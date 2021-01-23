from threading import local
import paramiko
import getpass
import socket
from sshtunnel import SSHTunnelForwarder
from Cryptodome.Cipher import AES

REMOTE_SERVER_IP = 'sunfire.comp.nus.edu.sg'
PRIVATE_SERVER_IP = '137.132.86.228'

KEY = b'\x01\x80\xba\x82\x7a\xc8\x7a\x3a\x26\xf1\xca\xc6\x9e\x1c\x3c\xbe'
cipher = AES.new(KEY, AES.MODE_EAX)

username = input("Enter ssh username: ")
password =  getpass.getpass("Enter ssh password: ")

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
            ciphertext, tag = cipher.encrypt_and_digest(message)

            mySocket.send(ciphertext.encode())
            data = mySocket.recv(1024).decode()
                
            print ('Received from server: ' + data)
                
            message = input(" -> ")
                 
        mySocket.close()
    

print('FINISH!')