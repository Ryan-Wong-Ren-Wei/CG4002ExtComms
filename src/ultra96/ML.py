import time
import sys
# import pandas
import os
# import pandas as pd
# import numpy as np
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

def handleML(inputQueue, output, moveCompletedFlag, evalClient):
    try:
        # test_model = load_model("MLP")
        print("Initializing ML model")
        tflite_model = tflite.Interpreter(model_path="model.tflite")
        tflite_model.allocate_tensors()
        print("Initialization done")
        while True:
            dataFrame = []
            if inputQueue.qsize() > 29: 
                print("queue > 40, processing data")
                for _ in range(30):
                    dataPoint = inputQueue.get()
                    dataPoint.pop('moveFlag')
                    dataPoint.pop('Id')
                    dataPoint.pop('Datetime')
                    dataFrame.append(dataPoint)
                print("dataframe retrieved")
                # print(dataFrame)
                pdDataFrame = pandas.DataFrame(dataFrame)
                print(pdDataFrame)
                data_to_evaluate = preprocess.process_data_stream(pdDataFrame)
                prediction = eval_mlp(data_to_evaluate, tflite_model)
                output = prediction
                print(output)
                evalClient.sendToEval(action=ENCODE[output],positions=1)
                moveCompletedFlag.set()
                while not inputQueue.empty():
                    inputQueue.get()
    except:
        print(sys.exc_info())
