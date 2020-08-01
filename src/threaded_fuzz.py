import parse
import json
import copy
import multiprocessing
from threading import Thread
from subprocess import *
from queue import Queue
from log import *

intcases = [-1, 0, 1, 10*(2**30), -10*(2**30)]
stringcases = ["A"*10, "A"*100, "A"*1000, "\'", "\"", "\\", " ", "\n", "`", ",", "/", "", "\0"]
formatcases = ["%n"*10, "%n"*100, "%1000000$x"]

allcases = [*intcases, *stringcases, *formatcases]

'''
Mutates the inputWords and adds it to the sendBuffer
'''
def createPayloads(inputWords: dict, sendBuffer: Queue):
    for i in range(len(inputWords['values'])):
        testcases = [inputWords['values'][i]] + allcases

        for case in testcases:
            payload = copy.deepcopy(inputWords)
            payload['values'][i] = case
            sendBuffer.put(payload)
            
def fastPayloads_temp(inputWords: dict, sendBuffer: Queue):
    sendBuffer.put(inputWords)
'''
Sends payloads from the sendBuffer to the binary
If crash is detected, payload is stored in crashBuffer
'''
def sendPayload(sendBuffer: Queue, crashBuffer: Queue):
    while True:
        words = sendBuffer.get()
        if words is None or not crashBuffer.empty():
            break

        inputString = parse.getInputFromDict(words)

        p = Popen(binary, stdin=PIPE, stdout=PIPE)
        output, error = p.communicate(inputString.encode())
        logger.debug(output.decode())
        if (error):
            logger.error(error)

        if p.returncode == -11:
            crashBuffer.put(inputString)

'''
Producer-consumer implemenation of gen_fuzz
#producers = 1, #consumers = #cores on the machine
'''
def threadedFuzz(_binary: str, inputWords: dict, fast_temp=False) -> str:
    # logger.info("starting threaded fuzz")
    global binary 
    binary = _binary

    # Match number of threads to number of logical cores
    cores = multiprocessing.cpu_count()
    sendBuffer = Queue()
    crashBuffer = Queue()

    # Single producer
    producer = Thread(target=createPayloads, args=[inputWords, sendBuffer])
    producer.start()

    # Multiple consumers
    consumers = [Thread(target=sendPayload, args=[sendBuffer, crashBuffer]) for i in range(cores)]
    for c in consumers:
        c.start()

    # Wait for producer to finish
    producer.join()

    # End all consumers
    for c in consumers:
        sendBuffer.put(None)
    for c in consumers:
        c.join()

    # logger.info("finished threaded fuzz")
    return None if crashBuffer.empty() else crashBuffer.get()