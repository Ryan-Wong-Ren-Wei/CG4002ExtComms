from Util.encryption import EncryptionHandler
import socket

class EvalClient():

    POSITIONS = ['1 2 3', '3 2 1', '2 3 1', '3 1 2', '1 3 2', '2 1 3']       
    ACTIONS = ['gun', 'sidepump', 'hair'] 

    def __init__(self, host:str, port:int, controlMain):
        self.controlMain = controlMain
        self.server = (host,port)
        self.encryptionHandler = EncryptionHandler(b'Sixteen byte key')
        pass

    def sendToEval(self, positions=None, action=None, sync_delay=None, quit=False):
        if quit:
            message = '# |logout| '
        else:
            message = '#' + self.POSITIONS[positions] + '|' + self.ACTIONS[action] + '|' + '0.005'

        message = self.encryptionHandler.encrypt_msg(message)
        self.evalSocket.send(message)
        data = self.evalSocket.recv(1024).decode()
        print ('Received from server: ' + data)

    def connectToEval(self):
        self.evalSocket = socket.socket()
        print(self.server)
        self.evalSocket.connect(self.server)

if __name__ == "__main__":
    evalClient = EvalClient('127.0.0.1', 8888, None)
    evalClient.connectToEval()
    command = input()
    while command != "quit":
        evalClient.sendToEval(1, 2, 0.05)
        command = input()
    evalClient.sendToEval(quit=True)
