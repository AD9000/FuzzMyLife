import parse
import mutator

from subprocess import *
import multiprocessing
import copy
from threading import Thread, Event
from queue import Queue
from log import *

sendBuffer = Queue()
crashBuffer = Queue()

def sendPayload(sendBuffer: Queue, crashBuffer: Queue):
    while True:
        if not crashBuffer.empty():
            break

        testInput = sendBuffer.get()
        if testInput is None:
            break

        ret, output, error = sendWithOutput(testInput)

        if (error):
            logger.debug(output)
            logger.error(error)

        if ret == -11:
            crashBuffer.put(testInput)

def sendWithOutput(inputBytes: bytes) -> (int, str, str):
    p = Popen(binary, stdin=PIPE, stdout=PIPE)

    try:
        output, error = p.communicate(inputBytes, timeout=1)
    except TimeoutExpired:
        p.kill()
        output, error = p.communicate()

    return p.returncode, output, error

def mutate(inputDict: dict, mutation) -> str:
    mutation(copy.deepcopy(inputDict))

def fuzzMyLife(inputDict: dict) -> str:
    mutator.setBuffers(sendBuffer, crashBuffer)

    num_senders = max(1, multiprocessing.cpu_count()-1)
    senders = [Thread(target=sendPayload, args=([sendBuffer, crashBuffer])) for i in range(num_senders)]
    for sender in senders:
        sender.start()

    mutations = mutator.getMutations()
    for mutation in mutations:
        mutatorThread = Thread(target=mutate, args=([inputDict, mutation]))
        mutatorThread.start()

        # hanging here for some reason? test early exit
        mutatorThread.join()

    crashBuffer.put(None)
    for sender in senders:
        sender.join()

    return None if crashBuffer.empty() else crashBuffer.get()

def setBinary(_binary: str):
    global binary
    binary = _binary