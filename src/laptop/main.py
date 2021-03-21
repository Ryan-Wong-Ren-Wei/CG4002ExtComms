from multiprocessing import Pool, Queue, Process, pool
from laptopClient import LaptopClient
# import internal_comms
import random
import time
import datetime

def blunoDummy(inputQueue):
    while True:
        for _ in range(60):
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
                        "moveFlag": 0
                    }
            inputQueue.put(dummy_packet)
            time.sleep(0.04)

        for _ in range(60):
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
                        "moveFlag": 1
                    }
            inputQueue.put(dummy_packet)
            time.sleep(0.05)


if __name__ == "__main__":
    client = LaptopClient("127.0.0.1", 10022, "shittyprogrammer")
    client.start(remote=False)
    inputQueue = Queue()
            
    # blunoProcess = Process(target=internal_comms.connect_to_pi, args=("p1", inputQueue, 0))
    blunoProcess = Process(target=blunoDummy, args=(inputQueue,))    
    handleBlunoDataProcess = Process(target=client.handleBlunoData, args=(inputQueue,))
    handleServerProcess = Process(target=client.handleServerCommands)
    try:
        blunoProcess.start()
        handleBlunoDataProcess.start()
        handleServerProcess.start()

        blunoProcess.join()
        handleBlunoDataProcess.join()
        handleServerProcess.join()
    except Exception as e:
        print("MAIN: ", e)
        blunoProcess.terminate()
        handleServerProcess.terminate()
        handleBlunoDataProcess.terminate()
    # client.handleBlunoData(inputQueue)
