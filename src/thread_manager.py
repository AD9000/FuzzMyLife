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

def sendPayload(sendBuffer: Queue, crashBuffer: Queue, timeout: int):
    while True:
        testInput = sendBuffer.get()
        if testInput is None or not crashBuffer.empty():
            break

        ret, output, error = sendWithOutput(testInput, timeout)

        if (error):
            logger.debug(output)
            # logger.error(error)

        if ret == -11:
            crashBuffer.put(testInput)

def sendWithOutput(inputBytes: bytes, timeout: int) -> (int, str, str):
    p = Popen(binary, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    try:
        output, error = p.communicate(inputBytes, timeout=timeout)
    except TimeoutExpired:
        logger.debug('kill')
        p.kill()
        output, error = p.communicate()

    ret = p.returncode

    return ret, output, error

def mutate(inputDict: dict, mutation) -> str:
    mutation(copy.deepcopy(inputDict))

def fuzzMyLife(inputDict: dict, runtime: int) -> str:
    mutator.setBuffers(sendBuffer, crashBuffer)

    num_senders = multiprocessing.cpu_count() * 2
    senders = [Thread(target=sendPayload, args=([sendBuffer, crashBuffer, 5+runtime])) for i in range(num_senders)]
    for sender in senders:
        sender.start()

    mutations = mutator.getMutations()
    for mutation in mutations:
        # logger.debug(mutation.__name__)
        mutatorThread = Thread(target=mutate, args=([inputDict, mutation]))
        mutatorThread.start()

        mutatorThread.join()

    for i in range(num_senders):
        sendBuffer.put(None)

    for sender in senders:
        sender.join()

    return None if crashBuffer.empty() else crashBuffer.get()

def setBinary(_binary: str):
    global binary
    binary = _binary