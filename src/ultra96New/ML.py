import time
import sys
import os
import tflite_runtime.interpreter as tflite
import numpy as np
import pandas

import preprocess
# from keras.models import load_model

DECODE = {0: "dab", 1: "listen", 2: "pointhigh"}
ENCODE = {"dab": 0, "listen": 1, "pointhigh": 2}

# class ML:
#     def __init__(self):
#         self.test_model = load_model("MLP")
        
#     def handleML(self, inputQueue):
#         while True:
#             dataFrame = []
#             if inputQueue.qsize() >= 50:
#                 for _ in range(50):
#                     dataFrame.append(inputQueue.get())

#             data_to_evaluate = preprocess.process_data_stream(dataFrame)

def eval_mlp(data, tflite_model):
    # receive data_segment
    """df_test = data
    X_test = df_test"""
    tflite_model.allocate_tensors()
    input_details = tflite_model.get_input_details()
    output_details = tflite_model.get_output_details()
    results = []
    # for data in X_val:
    data = data.reshape(input_details[0]['shape']).astype('float32')
    tflite_model.set_tensor(input_details[0]['index'], data)
    tflite_model.invoke()
    output_data = tflite_model.get_tensor(output_details[0]['index'])
    for x in output_data:
        maximum = 0
        for i in range(len(x)):
            if x[i] > maximum:
                answer = i
                maximum = x[i]

    return (DECODE[answer])

def handleML(dataQueues, outputForEval, globalShutDown, rdyForEval, dataQueueLock):
    try:
        # test_model = load_model("MLP")
        print("Initializing ML model")
        tflite_model = tflite.Interpreter(model_path="model.tflite")
        tflite_model.allocate_tensors()
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
                #loadscale
                mean = np.load("mean.npy")
                _scale = np.load("scale.npy")
                numMoves = [0,0,0]
                final_prediction = -1
                i = 0
                for dataFrame in dataFrames:
                    pdDataFrame = pandas.DataFrame(dataFrame)
                    #scale
                    data = (pdDataFrame - _mean)/_scale
                    data_to_evaluate = preprocess.process_data_stream(data)
                    prediction = eval_mlp(data_to_evaluate, tflite_model)
                    numMoves[prediction] += 1

                max_value = numpy.max(arr)
                final_prediction = np.where(arr == max_value)

                #prediction = random.randint(0,2)
                output = DECODE[final_prediction]
                outputForEval['action'] = final_prediction
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
