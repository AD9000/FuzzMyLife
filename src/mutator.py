import parse
import json
import copy

from queue import Queue
from log import *

intcases = [-1, 0, 1, 10*(2**20), -10*(2**20), 10*(2**30), -10*(2**30)]
stringcases = ["A"*10, "A"*100, "A"*1000, "\'", "\"", "\\", " ", "\n", "`", ",", "/", "", "\0"]
formatcases = ["%n"*10, "%n"*100, "%1000000$x"]

allcases = [*intcases, *stringcases, *formatcases]

def mutateValues(inputDict: dict):
    for i in range(len(inputDict['values'])):
        testcases = [inputDict['values'][i]]
        testcases.extend(allcases)

        for case in testcases:
            payload = copy.deepcopy(inputDict)
            payload['values'][i] = case
            sendBuffer.put(payload)

def mutateCSV(inputDict: dict):
    if inputDict['file'] != parse.FileType.CSV:
        return

    csvMutateCpl(copy.deepcopy(inputDict))

    for i in range(4):
        logger.info("+++++++++++ i = {} +++++++++++".format(i))

        values = copy.deepcopy(inputDict['values'])
        logger.info(values)
        inputDict['values'] = [*values, *values, *values]

        mutateValues(inputDict)
        csvMutateCpl(copy.deepcopy(inputDict))

        if not crashBuffer.empty():
            return

def csvMutateCpl(inputDict: dict):
    values = inputDict['values']
    for i in range(1, len(values)):
        if len(values) % i == 0:
            inputDict['cpl'] = i-1
            sendBuffer.put(inputDict)

def getMutations():
    return [mutateValues, mutateCSV]

def mutate(inputDict: dict, _sendBuffer: Queue, _crashBuffer: Queue) -> str:
    global sendBuffer
    global crashBuffer
    sendBuffer = _sendBuffer
    crashBuffer = _crashBuffer

    logger.info("running {}".format(mutator))
    mutator(copy.deepcopy(inputDict))