from multiprocessing import Pool, Queue, Process, pool
from laptopClient import LaptopClient
import internal_comms
import random
import time
import datetime
import sys

def blunoDummy(inputQueue):
    while True:
        for _ in range(150):
            dummy_packet = None
            dummy_packet = {
                        "Id": 1,
                        "GyroX": random.randint(-40000, 40000),
                        "GyroY": random.randint(-40000, 40000),
                        "GyroZ": random.randint(-40000, 40000),
                        "AccelX": random.randint(-40000, 40000),
                        "AccelY": random.randint(-40000, 40000),
                        "AccelZ": random.randint(-40000, 40000),
                        "time": time.time(),
                        "PosChangeFlag" : 0,
                        "moveFlag": 0
                    }
            inputQueue.put(dummy_packet)
            time.sleep(0.04)

        posChangeFlag = random.randint(-1,1)
        for _ in range(random.randint(1,2)):
            dummy_packet = {
                        "Id": 1,
                        "GyroX": random.randint(-40000, 40000),
                        "GyroY": random.randint(-40000, 40000),
                        "GyroZ": random.randint(-40000, 40000),
                        "AccelX": random.randint(-40000, 40000),
                        "AccelY": random.randint(-40000, 40000),
                        "AccelZ": random.randint(-40000, 40000),
                        "time": time.time(),
                        "PosChangeFlag" : posChangeFlag,
                        "moveFlag": 0
                    }
            inputQueue.put(dummy_packet)
            time.sleep(0.04)

        for _ in range(150):
            dummy_packet = None
            dummy_packet = {
                        "Id": 1,
                        "GyroX": random.randint(-40000, 40000),
                        "GyroY": random.randint(-40000, 40000),
                        "GyroZ": random.randint(-40000, 40000),
                        "AccelX": random.randint(-40000, 40000),
                        "AccelY": random.randint(-40000, 40000),
                        "AccelZ": random.randint(-40000, 40000),
                        "time": time.time(),
                        "PosChangeFlag" : 0,
                        "moveFlag": 1
                    }
            inputQueue.put(dummy_packet)
            time.sleep(0.04)


if __name__ == "__main__":
    dancerID = sys.argv[1].strip()
    client = LaptopClient("127.0.0.1", 10022, dancerID)
    remote = False
    if len(sys.argv) > 2 and sys.argv[2].strip() == "remote":
        client.start(remote=True)
    else:
        client.start()

    inputQueue = Queue()
            
    blunoProcess = Process(target=internal_comms.connect_to_pi, args=("p1", inputQueue, 0))
    # blunoProcess = Process(target=blunoDummy, args=(inputQueue,))    
    handleBlunoDataProcess = Process(target=client.handleBlunoData, args=(inputQueue,))
    handleServerProcess = Process(target=client.handleServerCommands)
    try:
        
        handleBlunoDataProcess.start()
        handleServerProcess.start()
        # input('press enter to start bluno')
        blunoProcess.start()

        blunoProcess.join()
        handleBlunoDataProcess.join()
        handleServerProcess.join()
    except Exception as e:
        print("MAIN: ", e)
        blunoProcess.terminate()
        handleServerProcess.terminate()
        handleBlunoDataProcess.terminate()
    # client.handleBlunoData(inputQueue)
