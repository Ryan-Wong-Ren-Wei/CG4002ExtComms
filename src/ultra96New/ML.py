import time
import sys
import os
import tflite_runtime.interpreter as tflite
import numpy as np
import pickle
import preprocess
from queue import Queue
from server import NUM_DANCERS
import sys
import pandas
import random 
# from keras.models import load_model
knn = pickle.load(open('knnpickle_file', 'rb'))

DECODE = {0: "gun", 1: "sidepump", 2: "hair"}
ENCODE = {"gun": 0, "sidepump": 1, "hair": 2}

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
    answer = 0
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

    return answer

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
                finalPred = [0,0,0]
                for dancerID in range(3):
                    dataQueue = dataQueues[dancerID]
                    dataFrame = []
                    for _ in range(30):
                        dataPoint = dataQueue.get()
                        dataFrame.append([dataPoint["GyroX"], dataPoint["GyroY"], dataPoint["GyroZ"]])
                    counts = [0, 0, 0]
                    count = 0
                    isHair = True
                    predictions = knn.predict_proba(dataFrame)
                    for h in predictions:
                        for j in range(3):
                            if h[j] >= 1:
                                counts[j] += 1
                    print(counts)
                    if counts[1] > 15:
                        pred = 1
                        finalPred[pred] += 1
                    elif counts[2] > 2 or counts[0] < 20:
                        pred = 2
                        finalPred[pred] += 1
                    else:
                        pred = 0
                        finalPred[pred] += 1
                    print(dancerID, pred)
                pred = finalPred.index(max(finalPred))
                print(DECODE[pred])
                outputForEval['action'] = pred
                rdyForEval.set()
                dataQueueLock.set()
                # doClockSync.set()
                for dataQueue in dataQueues:
                    while not dataQueue.empty():
                        dataQueue.get()
                # print("queue > 40, processing data")
            """if dataQueues[0].qsize() > 29 and dataQueues[1].qsize() > 29 and dataQueues[2].qsize() > 29: 
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
                _mean = np.load("mean.npy")
                _scale = np.load("scale.npy")
                numMoves = [0,0,0]
                final_prediction = -1
                i = 0
                maxi = 0
                for dataFrame in dataFrames:
                    pdDataFrame = pandas.DataFrame(dataFrame)
                    #scalr
                    data_to_evaluate = preprocess.process_data_stream(pdDataFrame)
                    data_scaled = (data_to_evaluate - _mean)/_scale
                    start = time.time()
                    prediction = eval_mlp(data_scaled, tflite_model)
                    print(time.time()-start)
                    numMoves[prediction] += 1
                    if numMoves[prediction] > maxi:
                        maxi = numMoves[prediction]
                        final_prediction = prediction
                    print(prediction)
                    print("END OF LOOP")

                #prediction = random.randint(0,2)
                output = DECODE[final_prediction]
                
                print(output)"""
                # evalClient.sendToEval(action=ENCODE[output],positions=1)
                
    except Exception as e:
        print("[ML.py][ERROR]", e)
        return
