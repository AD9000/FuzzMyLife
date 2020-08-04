import parse
import json
import copy

from queue import Queue
from threading import Event
from log import *

intcases = [-1, 0, 1, 10*(2**20), -10*(2**20), 10*(2**30), -10*(2**30)]
stringcases = ["A"*10, "A"*100, "A"*1000, "\'", "\"", "\\", " ", "\n", "`", ",", "/", "", "\0"]
formatcases = ["%n"*10, "%n"*100, "%1000000$x"]

allcases = [*intcases, *stringcases, *formatcases]

def mutateValues(inputDict: dict, start=0):
    if start > len(inputDict['values']):
        logger.error("value too large")
        return

    for i in range(start, len(inputDict['values'])):
        testcases = [inputDict['values'][i]]
        testcases.extend(allcases)

        payload = copy.deepcopy(inputDict)
        for case in testcases:
            payload['values'][i] = case

            sendBuffer.put(parse.getInputFromDict(payload))

def mutateCSV(inputDict: dict):
    if inputDict['file'] != parse.FileType.CSV:
        return

    csvMutateCpl(copy.deepcopy(inputDict))

    for i in range(4):
        logger.info("+++++++++++ i = {} +++++++++++".format(i))

        currLen = len(inputDict['values'])
        values = copy.deepcopy(inputDict['values'])
        inputDict['values'] = [*values, *values, *values]

        mutateValues(inputDict, currLen)
        csvMutateCpl(copy.deepcopy(inputDict))

        if not crashBuffer.empty():
            return

def csvMutateCpl(inputDict: dict):
    values = inputDict['values']
    for i in range(1, len(values)):
        if len(values) % i == 0:
            inputDict['cpl'] = i-1
            sendBuffer.put(parse.getInputFromDict(inputDict))


# try every byte value for every byte
# super smart
def bytemutate(inputDict: dict) -> bytes:
    inputBytes = parse.getInputFromDict(inputDict)
    for i in range(len(inputBytes)):
        if inputBytes[i] == b'\n' and inputDict['file'] in [parse.FileType.PLAINTEXT, parse.FileType.CSV]:
            # to not screw up number of lines required...
            continue
        for case in range(0, 0xff+1, 1):
            if i < len(inputBytes)-1:
                payload = inputBytes[:i] + case.to_bytes(1, 'little') + inputBytes[i+1:]
            else:
                payload = inputBytes[:i] + case.to_bytes(1, 'little')
            sendBuffer.put(payload)
            if not crashBuffer.empty():
                return

def getMutations():
    return [mutateValues, mutateCSV, bytemutate]

def setBuffers(_sendBuffer: Queue, _crashBuffer: Queue):
    global sendBuffer
    global crashBuffer
    sendBuffer = _sendBuffer
    crashBuffer = _crashBuffer