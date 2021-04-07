import internal_comms
from multiprocessing import Queue, Process
import threading
import time
import datetime
import logging
import sys
import multiprocessing
import random
import csv
import signal

tuple = Queue()
csv_buffer = []
file_directory = ""
move_name=""
interval=0

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
                    "MotionFlag": 1,
                }
        
        buffer_tuple.put(dummy_packet)
        time.sleep(0.05)
    
    
def write_to_csv(_name, tuple, arg2):
    global file_directory, move_name, interval
    dt = datetime.datetime.now()
    ts_str = dt.strftime("%m-%d-%Y-%H-%M-%S")
    file_directory = arg2+"-"+ts_str+".csv"
    move_name = arg2

    signal.signal(signal.SIGINT, signal_handler)
    packet = None
    while True:
        packet = None 
        packet = tuple.get()
    
        if packet is not None:
                
            if (packet["moveFlag"] != 0):
                csv_buffer.append(packet)
        else:
            print("No packet founds...")

def signal_handler(signal, frame):
    global file_directory, move_name, interval
    
    with open(file_directory, mode='w') as csv_file:
        fieldnames = ['GyroX', 'GyroY', 'GyroZ', 'AccelX', 'AccelY', 'AccelZ', 'moveFlag']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        for packet in csv_buffer:
                writer.writerow({'GyroX': packet["GyroX"],
                                 'GyroY': packet["GyroY"],
                                 'GyroZ': packet["GyroZ"],
                                 'AccelX': packet["AccelX"],
                                 'AccelY': packet["AccelY"],
                                 'AccelZ': packet["AccelZ"],
                                 'moveFlag': packet["moveFlag"],
                                 })
    sys.exit(0)
    
def main():
    ## for actual implementation, replace connect_to_dummy_internalComms wih internal_comms.connect_to_pi with 
    # p1 = Process(target=connect_to_dummy_internalComms, args=("p1", tuple, 0))
    p1 = Process(target=internal_comms.connect_to_pi, args=("p1", tuple, int(sys.argv[1])))    
    p2 = Process(target=write_to_csv, args=("p2",tuple, sys.argv[2]))
    p1.start()
    p2.start()
    p1.join()
    p2.join()


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("invalid argument! please input: beetle index, move name")
    time.sleep(5)
    main()
    
