import time
import sys
import pandas

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

def handleML(inputQueue):
    while True:
        dataFrame = []
        if inputQueue.qsize() >= 50:
            for _ in range(50):
                dataPoint = inputQueue.get()
                dataPoint.pop('moveFlag')
                dataFrame.append(dataPoint)
            # print(dataFrame)
            print(pandas.DataFrame(dataFrame))