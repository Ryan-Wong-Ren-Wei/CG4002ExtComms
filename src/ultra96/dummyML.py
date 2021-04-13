from queue import Queue
from server import NUM_DANCERS
import sys
import pandas
import random
import preprocess
DECODE = {0: "dab", 1: "listen", 2: "pointhigh"}
ENCODE = {"dab": 0, "listen": 1, "pointhigh": 2}

def handleML(dataQueues, outputForEval, globalShutDown, rdyForEval, dataQueueLock):
    try:
        # test_model = load_model("MLP")
        print("Initializing ML model")
        # tflite_model = tflite.Interpreter(model_path="model.tflite")
        # tflite_model.allocate_tensors()
        print("Initialization done")
        while True:
            if globalShutDown.is_set():
                return
            dataFrames = [None for _ in range(NUM_DANCERS)]
            if dataQueues[0].qsize() > 29 and dataQueues[1].qsize() > 29 and dataQueues[2].qsize() > 29: 
                # print("queue > 40, processing data")
                for dancerID in range(3):
                    dataQueue = dataQueues[dancerID]
                    dataFrame = []
                    for _ in range(30):
                        dataPoint = dataQueue.get()
                        dataPoint.pop('moveFlag')
                        dataPoint.pop('Id')
                        dataPoint.pop('time')
                        dataFrame.append(dataPoint)
                    dataFrames[dancerID] = dataFrame
                # print("dataframe retrieved")
                # print(dataFrame)
                for dataFrame in dataFrames:
                    pdDataFrame = pandas.DataFrame(dataFrame)
                    # print(pdDataFrame)
                prediction = random.randint(0,2)
                output = DECODE[prediction]
                outputForEval['action'] = prediction
                # print(output)
                # evalClient.sendToEval(action=ENCODE[output],positions=1)
                rdyForEval.set()
                dataQueueLock.set()
                # doClockSync.set()
                for dataQueue in dataQueues:
                    while not dataQueue.empty():
                        dataQueue.get()
    except:
        print(sys.exc_info())
        return
