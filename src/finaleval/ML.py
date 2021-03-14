import time
def eatQ(inputQueue):
    while True:
        data = inputQueue.get()
        print(data)
        time.sleep(1)