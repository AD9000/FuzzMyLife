import parse
import mutator

from subprocess import *
import multiprocessing
from threading import Thread
from queue import Queue
from log import *

sendBuffer = Queue()
crashBuffer = Queue()

def testerThread(sendBuffer: Queue, crashBuffer: Queue):
    while True:
        testInput = sendBuffer.get()
        if testInput is None or not crashBuffer.empty():
            break

        inputString = parse.getInputFromDict(testInput)

        p = Popen(binary, stdin=PIPE, stdout=PIPE)
        output, error = p.communicate(inputString.encode())

        if (error):
            logger.debug(output)
            logger.error(error)
        if p.returncode == -11:
            crashBuffer.put(inputString)

def sendWithOutput(inputDict: dict, binary) -> str:
    inputString = parse.getInputFromDict(inputDict)

    p = Popen(binary, stdin=PIPE, stdout=PIPE)
    return p.communicate(inputString.encode())

def initTesters() -> list:
    num_testers = max(1, multiprocessing.cpu_count()-1)
    testers = [Thread(target=testerThread, args=([sendBuffer, crashBuffer])) for i in range(num_testers)]
    for tester in testers:
        tester.start()

    return testers

def killTesters(testers: list):
    crashBuffer.put(None)
    
    for tester in testers:
        tester.join()

def initMutator(inputDict: dict):
    mutatorThread = Thread(target=mutator.mutate, args=([inputDict, sendBuffer, crashBuffer]))
    mutatorThread.start()

    return mutatorThread

def begin(inputDict: dict) -> str:
    testerThreads = initTesters()
    mutations = mutator.getMutations()

    for mutation in mutations:
        mutationThread = initMutator(inputDict)
        mutationThread.join()

    killTesters(testerThreads)

    return None if crashBuffer.empty() else crashBuffer.get()

def setBinary(_binary: str):
    global binary
    binary = _binary