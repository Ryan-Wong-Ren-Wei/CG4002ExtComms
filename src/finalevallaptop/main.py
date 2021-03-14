from multiprocessing import Queue, Process
from laptopClient import LaptopClient
import internal_comms

client = LaptopClient("127.0.0.1", 10022)
client.start()
inputQueue = Queue()
# for _ in range(50):
#     dummy_packet = None
#     dummy_packet = {
#                 "GyroX": random.randint(-40000, 40000),
#                 "GyroY": random.randint(-40000, 40000),
#                 "GyroZ": random.randint(-40000, 40000),
#                 "AccelX": random.randint(-40000, 40000),
#                 "AccelY": random.randint(-40000, 40000),
#                 "AccelZ": random.randint(-40000, 40000),
#                 "StartFlag": 1
#             }
    
blunoProcess = Process(target=internal_comms.connect_to_pi, args=("p1", tuple, 0))    
clientProcess = Process(target=client.handleBlunoData, args=("p2",inputQueue), type=type)
blunoProcess.start()
clientProcess.start()
blunoProcess.join()
clientProcess.join()
client.handleBlunoData(inputQueue)