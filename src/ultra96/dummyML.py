import sys
import pandas
import random
import preprocess
DECODE = {0: "dab", 1: "listen", 2: "pointhigh"}
ENCODE = {"dab": 0, "listen": 1, "pointhigh": 2}

def handleML(inputQueue, output, moveCompletedFlag, evalClient, globalShutDown, doClockSync):
    try:
        # test_model = load_model("MLP")
        print("Initializing ML model")
        # tflite_model = tflite.Interpreter(model_path="model.tflite")
        # tflite_model.allocate_tensors()
        print("Initialization done")
        while True:
            if globalShutDown.is_set():
                return
            dataFrame = []
            if inputQueue.qsize() > 29: 
                print("queue > 40, processing data")
                for _ in range(30):
                    dataPoint = inputQueue.get()
                    dataPoint.pop('moveFlag')
                    dataPoint.pop('Id')
                    dataPoint.pop('time')
                    dataFrame.append(dataPoint)
                print("dataframe retrieved")
                # print(dataFrame)
                pdDataFrame = pandas.DataFrame(dataFrame)
                print(pdDataFrame)
                data_to_evaluate = preprocess.process_data_stream(pdDataFrame)
                prediction = random.randint(0,2)
                output = DECODE[prediction]
                print(output)
                evalClient.sendToEval(action=ENCODE[output],positions=1)
                moveCompletedFlag.set()
                doClockSync.set()
                while not inputQueue.empty():
                    inputQueue.get()
    except:
        print(sys.exc_info())
