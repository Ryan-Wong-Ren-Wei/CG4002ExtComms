from random import randint
from server import NUM_DANCERS, Ultra96Server
from Util.encryption import EncryptionHandler
import socket
import threading

POSITIONS = ['1 2 3', '3 2 1', '2 3 1', '3 1 2', '1 3 2', '2 1 3']   
POSITIONS_DICT = {'1 2 3' : 0, '3 2 1' : 1, '2 3 1' : 2, '3 1 2' : 3, '1 3 2' : 4, '2 1 3' : 5}
ACTIONS = ['gun', 'sidepump', 'hair'] 

class EvalClient():
    def __init__(self, host:str, port:int, controlMain):
        self.controlMain = controlMain
        self.server = (host,port)
        self.encryptionHandler = EncryptionHandler(b'Sixteen byte key')
        pass

    def sendToEval(self, positions=randint(0,5), action=None, sync_delay=0, quit=False):
        if quit:
            message = '# |logout| '
        else:
            if positions == None:
                positions = randint(0,5)
            message = '#' + POSITIONS[positions] + '|' + ACTIONS[action] + '|' + str(sync_delay)

        message = self.encryptionHandler.encrypt_msg(message)
        self.evalSocket.send(message)

        if quit:
            return
            
        data = self.evalSocket.recv(1024).decode()
        print ('Received from server: ' + data)
        return data
    
    def updateDancerPositions(self, dancerPositions, positionChange):
        middleDancerIndex = int(dancerPositions[1]) - 1
        leftDancerIndex = int(dancerPositions[0]) - 1
        rightDancerIndex = int(dancerPositions[2]) - 1

        # middle dancer doesn't move
        if positionChange[middleDancerIndex] == 0:
            # all dancers don't move
            if positionChange[rightDancerIndex] == 0 and positionChange[leftDancerIndex] == 0:
                print("[UPDATE DANCER POSITIONS][NO CHANGE]", dancerPositions)
                positionChange = [0,0,0]
                return

            elif positionChange[rightDancerIndex] < 0 and positionChange[leftDancerIndex] > 0:
                temp = dancerPositions[0]
                dancerPositions[0] = dancerPositions[2]
                dancerPositions[2] = temp
                print("[UPDATE DANCER POSITIONS][RIGHT AND LEFT SWAP POSITIONS]", dancerPositions)
            
            else:
                print("[UPDATE DANCER POSITIONS][INVALID CHANGE]", dancerPositions)

        # middle dancer moves right
        elif positionChange[middleDancerIndex] > 0:
            if positionChange[leftDancerIndex] > 0 and positionChange[rightDancerIndex] < 0:
                dancerPositions[2] = middleDancerIndex + 1
                dancerPositions[0] = rightDancerIndex + 1
                dancerPositions[1] = leftDancerIndex + 1
                print("[UPDATE DANCER POSITIONS][MIDDLE & LEFT DANCERS MOVE RIGHT, RIGHT DANCER MOVES LEFT", dancerPositions)

            elif positionChange[leftDancerIndex] == 0 and positionChange[rightDancerIndex] < 0:
                dancerPositions[2] = middleDancerIndex + 1
                dancerPositions[1] = rightDancerIndex + 1
                print("[UPDATE DANCER POSITIONS][LEFT DANCER STAYS, MIDDLE DANCER MOVES RIGHT, RIGHT DANCER MOVES LEFT", dancerPositions)

            else:
                print("[UPDATE DANCER POSITIONS][INVALID CHANGE]", dancerPositions)

        #middle dancer moves left
        else:
            if positionChange[leftDancerIndex] > 0 and positionChange[rightDancerIndex] < 0:
                dancerPositions[0] = middleDancerIndex + 1
                dancerPositions[1] = rightDancerIndex + 1
                dancerPositions[2] = leftDancerIndex + 1
                print("[UPDATE DANCER POSITIONS][MIDDLE & RIGHT DANCERS MOVE LEFT, LEFT DANCER MOVES RIGHT", dancerPositions)

            elif positionChange[rightDancerIndex] == 0 and positionChange[leftDancerIndex] > 0:
                dancerPositions[0] = middleDancerIndex + 1
                dancerPositions[1] = leftDancerIndex + 1
                print("[UPDATE DANCER POSITIONS][RIGHT DANCER STAYS, MIDDLE DANCER MOVES LEFT, LEFT DANCER MOVES RIGHT", dancerPositions)

            else:
                print("[UPDATE DANCER POSITIONS][INVALID CHANGE]", dancerPositions)

        print("Positions updated, resetting position change")
        for x in range(len(positionChange)):
            positionChange[x] = 0

    def handleEval(self, outputForEval, rdyForEval : threading.Event, server: Ultra96Server,
        globalShutDown: threading.Event, dancerPositions: list, positionChange: list, doClockSync: threading.Event):

        while True:
            if globalShutDown.is_set():
                return
            try:
                rdyForEval.wait()
                self.updateDancerPositions(dancerPositions, positionChange)
                outputForEval['delay'] = server.getSyncDelay()
                positionsStr = ''
                for dancerPosition in dancerPositions:
                    positionsStr += str(dancerPosition) + ' '
                positionsStr = positionsStr.strip()
                
                outputForEval['positions'] = POSITIONS_DICT[positionsStr]
                print("SENDING TO EVAL SERVER: ", outputForEval)
                servResponse = self.sendToEval(outputForEval['positions'], outputForEval['action'], outputForEval['delay'])
                servResponse = servResponse.replace(',','')
                servResponse = servResponse.replace('[','')
                servResponse = servResponse.replace(']','')
                servResponse = servResponse.replace('\'','')
                servResponse = servResponse.replace(' ','')
                dancerPositions[0] = int(servResponse[0])
                dancerPositions[1] = int(servResponse[1])
                dancerPositions[2] = int(servResponse[2])
                print("Server updated values:", dancerPositions)
                rdyForEval.clear()  
                doClockSync.set()
                server.broadcastMessage("moveComplete")
            except Exception as e:
                print("[ERROR][EVALCLIENT]", e)
                return

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
