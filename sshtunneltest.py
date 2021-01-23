from threading import local
import paramiko
import getpass
import socket
from sshtunnel import SSHTunnelForwarder
REMOTE_SERVER_IP = 'sunfire.comp.nus.edu.sg'
PRIVATE_SERVER_IP = '137.132.86.228'

username = input("Enter ssh username: ")
password =  getpass.getpass("Enter ssh password: ")

with SSHTunnelForwarder(
    REMOTE_SERVER_IP,
    ssh_username=username,
    ssh_password=password,
    remote_bind_address=(REMOTE_SERVER_IP, 10022),
    local_bind_address=('localhost', 10022)
) as tunnel1:
    print('Tunnel opened to sunfire.comp.nus.edu.sg with...')
    print('Address: ' + str(tunnel1.local_bind_address))
    print('Port no: ' + str(tunnel1.local_bind_port))
    host = PRIVATE_SERVER_IP
    port = 10022
        
    mySocket = socket.socket()
    mySocket.connect((host,port))
        
    message = input(" -> ")
        
    while message != 'q':
            mySocket.send(message.encode())
            data = mySocket.recv(1024).decode()
                
            print ('Received from server: ' + data)
                
            message = input(" -> ")
                
    mySocket.close()
    

print('FINISH!')