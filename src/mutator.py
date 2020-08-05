import parse
import json
import copy
import xml.etree.ElementTree as ET

from fileTypes import *
from queue import Queue
from threading import Event
from log import *

intcases = [0, 10*2**20, -10*2**20, 10*2**30, -10*2**30]
# someone pls turn this into a beautiful one-line list comprehension
# for i in range(0, 21):
#     intcases.extend([2**i, -2**i])
intcases.extend(f(i) for i in range(21) for f in (lambda x: 2**x, lambda x: -2**x))
#:)
overflowcases = ["A"*(2**i) for i in range(2,15)]
stringcases = ["\'", "\"", "\\", " ", "\n", "`", ",", "/", "", "\0", "ふ", "😠"]
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


bytecases = []
bytecases.extend([x for x in range(0,0x20)])
bytecases.extend([x for x in range(0x21, 0x7f, 2)])
bytecases.extend([0x7f])
bytecases.extend([x for x in range(0x80, 0xff+1)])
# try every byte value for every byte
# super smart
def mutateBytes(inputDict: dict):
    inputBytes = parse.getInputFromDict(inputDict)
    for i in range(len(inputBytes)):
        if inputBytes[i] == b'\n' and inputDict['file'] in [FileType.PLAINTEXT, FileType.CSV]:
            # to not screw up number of lines required...
            continue
        for case in bytecases:
            if i < len(inputBytes)-1:
                payload = inputBytes[:i] + case.to_bytes(1, 'little') + inputBytes[i+1:]
            else:
                payload = inputBytes[:i] + case.to_bytes(1, 'little')
            sendBuffer.put(payload)
            if not crashBuffer.empty():
                return

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

def setBuffers(_sendBuffer: Queue, _crashBuffer: Queue):
    global sendBuffer
    global crashBuffer
    sendBuffer = _sendBuffer
    crashBuffer = _crashBuffer