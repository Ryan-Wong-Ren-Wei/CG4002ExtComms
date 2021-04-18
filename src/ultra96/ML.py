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
dabpoint = pickle.load(open('dab-pointhigh', 'rb'))
wipelisten = pickle.load(open('wipelisten', 'rb'))
DECODE = {0: "dab", 1: "elbowkick", 2: "gun", 3: "hair", 4: "listen", 5: "pointhigh", 6: "sidepump", 7: "wipetable"}
ENCODE = {"dab": 0, "elbowkick": 1, "gun": 2, "hair": 3, "listen": 4, "pointhigh": 5, "sidepump": 6, "wipetable": 7}
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

def handleML(dataQueues, outputForEval, globalShutDown, rdyForEval, dataQueueLock, doClockSync):
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
            if dataQueues[0].qsize() > 99 and dataQueues[1].qsize() > 99 and dataQueues[2].qsize() > 99:
                doClockSync.set()
                finalPred = [0,0,0,0,0,0,0,0]
                for dancerID in range(3):
                    dataQueue = dataQueues[dancerID]
                    dataFrame = []
                    lrFrame = []
                    for _ in range(100):
                        dataPoint = dataQueue.get()
                        dataFrame.append([dataPoint["GyroX"], dataPoint["GyroY"], dataPoint["GyroZ"]])
                        lrFrame.append([dataPoint["GyroX"], dataPoint["GyroY"], dataPoint["GyroZ"], dataPoint["AccelX"], dataPoint["AccelY"], dataPoint["AccelZ"]])
                    counts = [0,0,0,0,0,0,0,0]
                    count = 0
                    isHair = True
                    predictions = knn.predict(dataFrame)
                    for h in predictions:
                        counts[h] +=1 
                    pred = counts.index(max(counts))
                    print(counts)
                    if pred == 0 or pred == 5 or pred == 1:
                        counts =  [0,0,0,0,0,0,0,0]
                        predictions = dabpoint.predict(dataFrame)
                        for h in predictions:
                            counts[h] +=1 
                        pred = counts.index(max(counts))
                        counts[5] = counts[2]
                        counts[2] = 0
                    if pred == 4:
                        counts =  [0,0,0,0,0,0,0,0]
                        predictions = wipelisten.predict(dataFrame)
                        for h in predictions:
                            counts[h] +=1 
                        pred = counts.index(max(counts))
                        counts[7] = counts[1]
                        counts[4] = counts[0]
                        counts[1] = 0
                        counts[0] = 0

                    for i in range(8):
                        finalPred[i] += counts[i]
                    print(counts)
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
                
    except:
        print(sys.exc_info())
        return
