import time
import sys
import pandas
import os
import pandas as pd
import numpy as np

import preprocess
from keras.models import load_model

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

def eval_mlp(data, test_model):
    # receive data_segment
    df_test = data
    X_test = df_test

    Y_pred = test_model.predict(X_test)
    Y_pred = np.argmax(Y_pred, axis=1)

    y_final = np.array([])

    for moves in Y_pred:
        y_final = np.append(y_final, DECODE[moves])

    print(y_final)

    return y_final

def handleML(inputQueue, output):
    test_model = load_model("MLP")
    while True:
        dataFrame = []
        if inputQueue.qsize() >= 40:
            for _ in range(40):
                dataPoint = inputQueue.get()
                dataPoint.pop('moveFlag')
                dataFrame.append(dataPoint)
            # print(dataFrame)
            pdDataFrame = pandas.DataFrame(dataFrame)
            print(pdDataFrame)
            data_to_evaluate = preprocess.process_data_stream(pdDataFrame)
            prediction = eval_mlp(data_to_evaluate, test_model)
            output = prediction[0]