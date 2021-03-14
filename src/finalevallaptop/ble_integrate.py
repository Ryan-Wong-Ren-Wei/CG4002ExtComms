# import internal_comms
from multiprocessing import Queue, Process
import threading
import time
import datetime
import logging
import sys
import multiprocessing
import random

tuple = Queue()

def connect_to_dummy_internalComms(_name, buffer_tuple, index):
    
    while True:
        dummy_packet = None
        dummy_packet = {
                    "Id": index,
                    "GyroX": random.randint(-40000, 40000),
                    "GyroY": random.randint(-40000, 40000),
                    "GyroZ": random.randint(-40000, 40000),
                    "AccelX": random.randint(-40000, 40000),
                    "AccelY": random.randint(-40000, 40000),
                    "AccelZ": random.randint(-40000, 40000),
                    "StartFlag": 1,
                    "Datetime": datetime.datetime.now()
                }
        
        buffer_tuple.put(dummy_packet)
        time.sleep(0.05)
    
    
def connect_to_ultra96(_name, tuple, type):
    
    
    logging.basicConfig(filename='ble_integrate.log',
                        filemode='w', level=logging.DEBUG)
    packet = None
    while True:
        packet = None 
        packet = tuple.get()
    
        if packet is not None:
            logging.debug("{}: Sending new packet: {}".format(datetime.datetime.now(), packet))
            print(packet)
        else:
            print("No packet founds...")
            
def main(type='local'):
    ## for actual implementation, replace connect_to_dummy_internalComms wih internal_comms.connect_to_pi with 
    p1 = Process(target=connect_to_dummy_internalComms, args=("p1", tuple, 0))
#     p1 = Process(target=internal_comms.connect_to_pi, args=("p1", tuple, 0))    
    p2 = Process(target=connect_to_ultra96, args=("p2",tuple), type=type)
    p1.start()
    p2.start()
    p1.join()
    p2.join()


if __name__ == '__main__':
    time.sleep(3)
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
