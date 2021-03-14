from multiprocessing import Queue, Process
from laptopClient import LaptopClient
# import internal_comms
import random
import time

def blunoDummy(inputQueue):
    for _ in range(50):
        dummy_packet = None
        dummy_packet = {
                    "GyroX": random.randint(-40000, 40000),
                    "GyroY": random.randint(-40000, 40000),
                    "GyroZ": random.randint(-40000, 40000),
                    "AccelX": random.randint(-40000, 40000),
                    "AccelY": random.randint(-40000, 40000),
                    "AccelZ": random.randint(-40000, 40000),
                    "moveFlag": 0
                }
        inputQueue.put(dummy_packet)
    time.sleep(5)

    for _ in range(50):
        dummy_packet = None
        dummy_packet = {
                    "GyroX": random.randint(-40000, 40000),
                    "GyroY": random.randint(-40000, 40000),
                    "GyroZ": random.randint(-40000, 40000),
                    "AccelX": random.randint(-40000, 40000),
                    "AccelY": random.randint(-40000, 40000),
                    "AccelZ": random.randint(-40000, 40000),
                    "moveFlag": 1
                }
        inputQueue.put(dummy_packet)

    for _ in range(50):
        dummy_packet = None
        dummy_packet = {
                    "GyroX": random.randint(-40000, 40000),
                    "GyroY": random.randint(-40000, 40000),
                    "GyroZ": random.randint(-40000, 40000),
                    "AccelX": random.randint(-40000, 40000),
                    "AccelY": random.randint(-40000, 40000),
                    "AccelZ": random.randint(-40000, 40000),
                    "moveFlag": 0
                }
        inputQueue.put(dummy_packet)
    time.sleep(5)

    for _ in range(50):
        dummy_packet = None
        dummy_packet = {
                    "GyroX": random.randint(-40000, 40000),
                    "GyroY": random.randint(-40000, 40000),
                    "GyroZ": random.randint(-40000, 40000),
                    "AccelX": random.randint(-40000, 40000),
                    "AccelY": random.randint(-40000, 40000),
                    "AccelZ": random.randint(-40000, 40000),
                    "moveFlag": 1
                }
        inputQueue.put(dummy_packet)
    time.sleep(5)

    for _ in range(50):
        dummy_packet = None
        dummy_packet = {
                    "GyroX": random.randint(-40000, 40000),
                    "GyroY": random.randint(-40000, 40000),
                    "GyroZ": random.randint(-40000, 40000),
                    "AccelX": random.randint(-40000, 40000),
                    "AccelY": random.randint(-40000, 40000),
                    "AccelZ": random.randint(-40000, 40000),
                    "moveFlag": 0
                }
        inputQueue.put(dummy_packet)
    time.sleep(5)

    for _ in range(50):
        dummy_packet = None
        dummy_packet = {
                    "GyroX": random.randint(-40000, 40000),
                    "GyroY": random.randint(-40000, 40000),
                    "GyroZ": random.randint(-40000, 40000),
                    "AccelX": random.randint(-40000, 40000),
                    "AccelY": random.randint(-40000, 40000),
                    "AccelZ": random.randint(-40000, 40000),
                    "moveFlag": 1
                }
        inputQueue.put(dummy_packet)
    time.sleep(5)

if __name__ == "__main__":
    client = LaptopClient("127.0.0.1", 10022, "shittyprogrammer")
    client.start()
    inputQueue = Queue()
            
    # blunoProcess = Process(target=internal_comms.connect_to_pi, args=("p1", inputQueue, 0))
    blunoProcess = Process(target=blunoDummy, args=(inputQueue,))    
    handleBlunoDataProcess = Process(target=client.handleBlunoData, args=(inputQueue,))
    handleServerProcess = Process(target=client.handleServerCommands)
    blunoProcess.start()
    handleBlunoDataProcess.start()
    handleServerProcess.start()

    blunoProcess.join()
    handleBlunoDataProcess.join()
    handleServerProcess.join()
    # client.handleBlunoData(inputQueue)
