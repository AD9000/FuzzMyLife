import parse
import json
import copy
import xml.etree.ElementTree as ET

from fileTypes import *
from queue import Queue
from threading import Event
from log import *

import random


intcases = [0, 2**31-1, -2**31, 2**32-1, -(2**32-1), 10*2**20, -10*2**20, 10*2**30, -10*2**30]
# someone pls turn this into a beautiful one-line list comprehension
# for i in range(0, 21):
#     intcases.extend([2**i, -2**i])
intcases.extend(f(i) for i in range(21) for f in (lambda x: 2**x, lambda x: -2**x))
#:)
overflowcases = ["A"*(2**i) for i in range(2,15)]
stringcases = ["\'", "\"", "\\", " ", "\n", "`", ",", "/", "", "\0", "ふ", "😠", "🐨", "}", ";"] # "{" breaks Python's xml parser
formatcases = ["%n"*10, "%n"*100, "%1000000$x"]

allcases = [*intcases, *overflowcases, *stringcases, *formatcases]

def mutateValues(inputDict: dict, start=0):
    if start > len(inputDict['values']):
        logger.error("value too large")
        return

    for i in range(start, len(inputDict['values'])):
        testcases = [inputDict['values'][i]]
        testcases.extend(allcases)

        tmp = inputDict['values'][i]
        for case in testcases:
            if not crashBuffer.empty():
                return

            inputDict['values'][i] = case
            sendBuffer.put(parse.getInputFromDict(inputDict))

        inputDict['values'][i] = tmp

def mutateCSV(inputDict: dict):
    if inputDict.get('file') != FileType.CSV:
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


# if short, want to try more values for each
# if long, want to test more places
# so first test some values for a large number of places
# then test more values for those places
# then more
# if its short, we'll have time to get through all cases
# if long, we will have tested a variety of places
# actually I'm going through every case, but in random order. that should achieve the above as well.
bcases = [x for x in range(0xff+1)]

def mutateBytes(inputDict: dict):
    inputBytes = parse.getInputFromDict(inputDict)
    cases = [(i, j) for i in range(len(inputBytes)) for j in range(len(bcases))] # takes ~.2 seconds to generate list for (500, 0x100)
    random.shuffle(cases)
    removes = []
    for case in cases:
        print(case)
        index = case[0]
        byte = case[1]
        if inputBytes[index] == b'\n' and inputDict['file'] in [FileType.PLAINTEXT, FileType.CSV]:
            # to not screw up number of lines required...
            continue
        # remove byte
        if index not in removes:
            payload = inputBytes[:index] + inputBytes[index+1:]
            sendBuffer.put(payload)
            removes.extend([index])
        # replace byte
        if index < len(inputBytes)-1:
            # replace byte
            replacepayload = inputBytes[:index] + byte.to_bytes(1, 'little') + inputBytes[index+1:]
            # insert byte
            # insertpayload = inputBytes[:i] + case.to_bytes(1, 'little') + inputBytes[i:]
        else:
            replacepayload = inputBytes[:index] + byte.to_bytes(1, 'little')
            # insertpayload = inputBytes + case.to_bytes(1, 'little')
        sendBuffer.put(replacepayload)
        # sendBuffer.put(insertpayload)
        # if not crashBuffer.empty()

def multiplyJSON(inputDict: dict, repeatTimes: int=15):
    if inputDict.get('file') != FileType.JSON:
        return

    rawJson = parse.getInputFromDict(inputDict)
    jsonObj = json.loads(rawJson)
    multiplier = 1
 
    for _ in range(repeatTimes):
        multiplier *= 2
        inputString = json.dumps([jsonObj] * multiplier)
        sendBuffer.put(inputString.encode())

def multiplyXML(inputDict: dict, maxMultiplier: int = 15):
    if inputDict.get('file') != FileType.XML:
        return
    
    rawXml = ET.ElementTree(ET.fromstring(parse.getInputFromDict(inputDict)))
    multiplier = 1
    root = rawXml.getroot()
    newRoot = copy.deepcopy(root)

    # at 2^15, the xml input is already 10Mb long 
    for _ in range(maxMultiplier):
        multiplier *= 2
        newRoot.extend(list(root) * multiplier)
        inputString = ET.tostring(newRoot)
        sendBuffer.put(inputString)

def invalidMultiplyInput(inputDict: dict, repeatTimes: int = 15):
    rawInput = parse.getInputFromDict(inputDict)
    multiplier = 1

    for _ in range(repeatTimes):
        multiplier *= 2
        inputString = rawInput * multiplier
        sendBuffer.put(inputString.encode())

def getMutations():
    return [mutateValues, mutateCSV, multiplyXML, multiplyJSON, mutateBytes]
    # return [mutateBytes]
def setBuffers(_sendBuffer: Queue, _crashBuffer: Queue):
    global sendBuffer
    global crashBuffer
    sendBuffer = _sendBuffer
    crashBuffer = _crashBuffer