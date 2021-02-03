import socket

host = '127.0.0.1'
port = 10022
key = 'Sixteen byte key'
    
socketList = []
for _ in range(3):
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mySocket.connect((host,port))   
    socketList.append(mySocket)

command = input("Enter as follows: Dancer ID|Message -> ")
while command != "quit":
    command = command.split("|")
    currSocket = socketList[int(command[0])]
    print(currSocket)
    currSocket.send(command[1].encode())
    command = input("Enter as follows: Dancer ID|Message -> ")

for socket in socketList:
    socket.close()
print("Quitting now")