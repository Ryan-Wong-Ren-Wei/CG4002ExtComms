from bluepy.btle import Scanner, DefaultDelegate, Peripheral, BTLEException, BTLEDisconnectError, ADDR_TYPE_RANDOM
from multiprocessing import Queue, Process
import threading
import time
import datetime
import logging
import signal
import sys
import multiprocessing

SLEEP_SEC = 0.03  # 30ms
LONG_SLEEP_SEC = 0.04  # for handshaking 40ms
SHORT_SLEEP_SEC = 0.02  # 5ms

blunoAddress = ['80:30:dc:e9:08:8b', '80:30:dc:d9:0c:a7', '80:30:dc:d9:23:3d']
#blunoAddress = ['34:14:b5:51:d6:0c', '34:b1:f7:d2:35:f3', '34:14:b5:51:d6:4e']
blunoHandshake = [0, 0, 0]
connections = [None]
serviceChars = [None]

tuple = Queue()

def calculateChecksum(str):
    result = 0
    for char in str:
        result ^= ord(char)
    return result

class BleConnectionError(Exception):
    # Base class ble connection error
    def __init__(self, message="Ble connection error!"):
        print(message)


class HandshakeError(Exception):
    def __init__(self, message="Handshake error"):
        print(message)


class DataProcessingError(Exception):
    def __init__(self, message="Data processing error!"):
        print(message)
        
def printAlert(msg):
    print("***************************************** {} **************************************".format(msg))

def sendH(serviceChar):
    try:
        serviceChar.write(bytes('H', "utf-8"))
        return True
    except:
        print("Fail sending H packet to bluno")
        return False


def sendR(serviceChar):
    try:
        serviceChar.write(bytes('R', "utf-8"))
        return True
    except:
        print("Fail sending R packet to bluno")
        return False


def sendC(serviceChar):
    try:
        serviceChar.write(bytes('C', "utf-8"))
        return True
    except:
        print("Fail sending C packet to bluno")
        return False
    

def waitForAllConnections(blunoId):
    global blunoHandshake
    print("Connection Status: {} ".format(str(blunoHandshake)))
    if sum(blunoHandshake) != len(blunoAddress) and blunoHandshake[blunoId] == 1:
        time.sleep(LONG_SLEEP_SEC)

def establishConnection(index, buffer_tuple):
    global connections, serviceChars
    addr = blunoAddress[index]
    print("Connecting to bluno " + str(index) +
          " with ip address: " + str(addr))
    connection_attempt_count = 0
    while True:
        try:
            p = Peripheral(addr)
            p.withDelegate(NotificationDelegate(index, buffer_tuple))
            blunoService = p.getServiceByUUID(
                "0000dfb0-0000-1000-8000-00805f9b34fb")
            serviceChar = blunoService.getCharacteristics()[0]
            connections[index] = p
            serviceChars[index] = serviceChar
            print("Connected to " + str(index))
            break

        except Exception as e:
            print(e)
            connection_attempt_count += 1
            print("Established connection with bluno {}, attempt {}...".format(
                str(index), str(connection_attempt_count)))
            time.sleep(LONG_SLEEP_SEC)
            continue

def performHandshake(index):
    global blunoHandshake
    global connections, serviceChars
    global clearIncomingSerialFlag
    handshake_count = 0
    while blunoHandshake[index] == 0 and handshake_count <= 5:
        print("Performing handshake with bluno " + str(index))
        # wait for notification
        try:
            if not sendH(serviceChars[index]):
                raise HandshakeError(
                    "Failed sending H, there is a connection error.")

            # Wait for arduino to response
            time.sleep(SHORT_SLEEP_SEC)

            if(connections[index].waitForNotifications(5)):
                if blunoHandshake[index] == 1:
                    print("Handshake with bluno " +
                          str(index) + " is completed\n\n")
                    break
                else:
                    print(
                        "I received something else, but blunoHandshake[index] == 0...")
                    print(blunoHandshake)
            else:
                print("Failed waitForNotification...")

        except Exception as e:
            print(e)
            break

        handshake_count += 1
        print("Didn't receive ACK from bluno {}, attempt {}...".format(
            str(index), str(handshake_count)))
        time.sleep(SLEEP_SEC)


def reconnect(index, buffer_tuple):
    global blunoHandshake
    global connections
    print("\n\n#################### Reconnecting to bluno " +
          str(index) + " ###################\n\n")
    reconnection_attempts = 0
    blunoHandshake[index] = 0
    connections[index] = None
    reconnection_count = 0

    while True:
        try:
            establishConnection(index, buffer_tuple)
            performHandshake(index)
            break

        except Exception as e:
            print(e)
            reconnection_attempts += 1
            print("Error! Reconnection attempt {} failed. Try again... ----------------------".format(reconnection_attempts))
            time.sleep(SLEEP_SEC)
            continue

        reconnection_attempts += 1
        print("Reconnection attempt {}...".format(
            str(index), str(reconnection_attempts)))
        time.sleep(SLEEP_SEC)
    print("\n\n#################### Successfully reconnected to bluno " +
          str(index) + " ###################\n\n")


class NotificationDelegate(DefaultDelegate):

    def __init__(self, index, buffer_tuple):
        DefaultDelegate.__init__(self)
        self.index = index
        self.buffer_str = ""
        self.buffer_tuple = buffer_tuple

    def handleNotification(self, cHandle, rawData):
        global blunoHandshake

        data = rawData.decode("utf-8")
        
        printAlert("Handling notification")
        print('Connection Index:' + str(self.index))
        print("Receive data from bluno" + str(self.index) + ": " + data)
        print(blunoHandshake)
        if data == "ACK":
            if blunoHandshake[self.index] == 0:
                print("Successfully received ACK from Bluno!")
                sendR(serviceChars[self.index])
                blunoHandshake[self.index] = 1
            else:
                print("Duplicate ACK...")
                sendR(serviceChars[self.index])
                blunoHandshake[self.index] = 1

        elif "ACK" in data:
            print("Data containing ACK!")
            blunoHandshake[self.index] = 1
            sendR(serviceChars[self.index])

        elif blunoHandshake[self.index] == 1:
            self.handleData(data)
        else:
            pass

    def handleData(self, data):
        self.buffer_str += data
        remaining_str = self.postProcessing(index=self.index, data=self.buffer_str)
        self.buffer_str = remaining_str
        
    
    def postProcessing(self, index, data):
        MAX_DATA_LENGTH = 70
        END_FLAG = "\n"
        DELIMITER = ";"
        CHECKSUM_DELIMITER = ":"

        buffer = ""
        if len(data) < 1:
            return ""

        # check last char
        if(data[-1] != END_FLAG):
            # Incompleted data, buffer it
            if (len(data) < MAX_DATA_LENGTH):
                return data

        # process data
        dt = datetime.datetime.now()
        dt = dt.strftime("%m/%d/%Y, %H:%M:%S")
        packets = data.split(END_FLAG)

        # no delimiter is found in split(), drop the whole buffer
        if len(packets) == 1:
            print("No END_FLAG exists for a long enough data stream, drop all buffer")
            return ""

        # if last packet is incompleted, buffer it
        if packets[-1] != "":
            # buffer incomplete packet
            buffer = packets[-1]

        # remove last token from processing, since it is either buffered or empty
        packets.pop()

        for i in range(len(packets)):
            packet = packets[i]

            print("Packet {}: {}".format(i, packet))

            # last token or empty packet(very unlikely but possible if \n\n)
            if packet == "":
                continue

            try:
                tokens = packet.split(CHECKSUM_DELIMITER)

                checksum_received = int(tokens[1])
                checksum_computed = calculateChecksum(tokens[0])

                if checksum_received != checksum_computed:
                    raise DataProcessingError(
                        "Packet corrupted! Checksum doesn't match!\n\
                         Checksum received: {}\n\
                         Checksum computed: {}\n"
                        .format(checksum_received, checksum_computed))

                print("Check sum passed!")

                content_tokens = tokens[0].split(DELIMITER)

                if len(content_tokens) != 7:
                    raise DataProcessingError(
                        "Packet corrupted! There are {} tokens (excluding checksum)".format(len(content_tokens)))

                start_flag = int(content_tokens[6])

                gyro_data_arr = [
                    int(content_tokens[0]),
                    int(content_tokens[1]),
                    int(content_tokens[2])
                ]

                accel_data_arr = [
                    int(content_tokens[3]),
                    int(content_tokens[4]),
                    int(content_tokens[5])
                ]

            except Exception as e:
                print("Data corrupted! Parsing error: \n" + str(e))
                continue

            packet = {
                "Id": index,
                "GyroX": gyro_data_arr[0],
                "GyroY": gyro_data_arr[1],
                "GyroZ": gyro_data_arr[2],
                "AccelX": accel_data_arr[0],
                "AccelY": accel_data_arr[1],
                "AccelZ": accel_data_arr[2],
                "StartFlag": start_flag,
                "Datetime": dt
            }
            print(packet)
            self.buffer_tuple.put(packet)

        return buffer

def connect_to_pi(_name, buffer_tuple, index):
    global connections
    establishConnection(index, buffer_tuple)
    performHandshake(index)

    # wait for incoming packet
    start_t = time.time()
    last_c_packet_t = time.time()
    while True:
        try:
            if(connections[index].waitForNotifications(1)):
                print("bluno {0} start time updated to {1}".format(
                    index, start_t))
                start_t = time.time()
                curr_t = time.time()
                if curr_t - start_t >= 3:
                    print("bluno {} packet delay more than 3 seconds, performing reconnection...".format(
                        index))
                    reconnect(index, buffer_tuple)
                if curr_t - last_c_packet_t >= 5:
                    print("Sending packet C to bluno {} at {}, last packet sent at {}, interval is {} seconds"
                            .format(str(index),
                                    str(int(curr_t)),
                                    str(int(last_c_packet_t)),
                                    str(int(curr_t - last_c_packet_t))))
                    last_c_packet_t = time.time()

                    # Send packet C to bluno to indicate a stable connection
                    if not sendC(serviceChars[index]):
                        raise BleConnectionError(
                            "Failed sending C packet, there is a connection error.")
			
            time.sleep(0.01)
	
        except Exception as e:
            print("Expection: " + str(e))
            reconnect(index, buffer_tuple)
            start_t = time.time()

#         waitForAllConnections(index)

def connect_to_ultra96(_name, tuple ):
    # TODO: Connect to ultra96
    logging.basicConfig(filename='ble_integrate.log',
                        filemode='w', level=logging.DEBUG)
    packet = None
    while True:
        packet = None 
        packet = tuple.get()
    
        if packet is not None:
            logging.debug("{}: Sending new packet: {}".format(datetime.now(), packet))

# def main():
#     p1 = Process(target=connect_to_pi, args=("p1", tuple, 0))
#     p2 = Process(target=connect_to_ultra96, args=("p2",tuple))
#     p1.start()
#     p2.start()
#     p1.join()
#     p2.join()
# 
# 
# if __name__ == '__main__':
#     time.sleep(3)
#     main()

