import parse
import json
import copy
import xml.etree.ElementTree as ET

from fileTypes import *
from queue import Queue
from threading import Event
from log import *

import random
import sys
import collections
from typing import List


intcases = [0, 2**31-1, -2**31, 2**32-1, -(2**32-1), 10*2**20, -10*2**20, 10*2**30, -10*2**30]
intcases.extend(f(i) for i in range(21) for f in (lambda x: 2**x, lambda x: -2**x))
#:)
overflowcases = ["A"*(2**i) for i in range(2,15)]
stringcases = ["\'", "\"", "\\", " ", "\n", "`", ",", "/", "", "\0", "ふ", "😠", "🐨", "}", ";", "X "*10] # "{" breaks Python's xml parser
stringcases.extend([" ".join(stringcases)])
formatcases = ["%n"*10, "%n"*100, "%1000000$x"]

allcases = [*intcases, *overflowcases, *stringcases, *formatcases]

# what is start for
def mutateValues(inputDict: dict, start=0):
    logger.debug('Mutate values')
    if start > len(inputDict['values']):
        logger.error("value too large")
        return

    for fieldType in ['values', 'tags']:
        if fieldType not in inputDict:
            continue
        for i in range(start, len(inputDict[fieldType])):
            testcases = allcases

            tmp = inputDict[fieldType][i]
            for case in testcases:
                if not crashBuffer.empty():
                    return

                inputDict[fieldType][i] = case
                sendBuffer.put(parse.getInputFromDict(inputDict))
                # logger.debug(parse.getInputFromDict(inputDict))

            inputDict[fieldType][i] = tmp

def mutateCSV(inputDict: dict):
    if inputDict.get('file') != FileType.CSV:
        return
    logger.debug('Multiply CSV')
    

    csvMutateCpl(copy.deepcopy(inputDict))

    for i in range(4):
        logger.debug("+++++++++++ i = {} +++++++++++".format(i))

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
# I'm going through every case, but in random order. that should achieve the above distribution.
bcases = [x for x in range(0xff+1)]

def mutateBytes(inputDict: dict):
    logger.debug('Mutate bytes')
    inputBytes = parse.getInputFromDict(inputDict)
    cases = [(i, j) for i in range(len(inputBytes)) for j in range(len(bcases))] # takes ~.2 seconds to generate list for (500, 0x100)
    random.shuffle(cases)
    removes = []
    for case in cases:
        # logger.debug(case)
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
            insertpayload = inputBytes[:index] + byte.to_bytes(1, 'little') + inputBytes[index:]
        else:
            replacepayload = inputBytes[:index] + byte.to_bytes(1, 'little')
            insertpayload = inputBytes + byte.to_bytes(1, 'little')
        sendBuffer.put(replacepayload)
        sendBuffer.put(insertpayload)
        # if not crashBuffer.empty(): return # should do this or no? It's slow I think.

def multiplyJSON(inputDict: dict, repeatTimes: int=15):
    if inputDict.get('file') != FileType.JSON:
        return
    logger.debug('Multiply JSON')

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
    logger.debug('Multiply XML')
    
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

def deepXML(inputDict: dict, maxMultiplier: int = 20):
    if (inputDict.get('file') != FileType.XML):
        return

    tree = ET.fromstring(parse.getInputFromDict(inputDict))

    # finding a leaf node
    parent, child = [None, None]
    root = tree
    while (True):
        parent, child, *_ = root.iter()
        if len(child) == 0:
            break

        root = child

    # getting the raw xml tag
    # by adding to child once
    parent = child
    child = copy.deepcopy(child)
    parent.append(child)

    # manual parsing go brr
    treeString = ET.tostring(tree).decode()
    parentString = ET.tostring(parent).decode()
    childString = ET.tostring(child).decode()

    head, tail = treeString.split(parentString)

    startTag, endTag = parentString.split(childString)

    multiplier = 1
    for _ in range(maxMultiplier):
        multiplier*=2
        inputString = head + startTag*multiplier + childString + endTag*multiplier + tail
        sendBuffer.put(inputString.encode())

def longJSONList(inputDict: dict, maxMultiplier: int = 20):
    if (inputDict.get('file') != FileType.JSON):
        return
    
    logger.info("Running: Long JSON list...")

    j = json.loads(parse.getInputFromDict(inputDict))
    listKeys = []
    for key in j:
        if isinstance(j[key], list):
            hasList = True
            listKeys.append(key)
    
    if len(listKeys) == 0:
        j["AFDSFDSADSAFDSA"] = ["A"]
        listKeys.append("AFDSFDSADSAFDSA")
    
    for key in listKeys:
        inputObj = copy.deepcopy(j)
        for _ in range(2, maxMultiplier):
            if len(inputObj[key]) == 0:
                inputObj[key].append("B")
            inputObj[key].extend(inputObj[key])
            sendBuffer.put(json.dumps(inputObj).encode())


def invalidMultiplyInput(inputDict: dict, repeatTimes: int = 15):
    logger.debug('Syntax-less multiply')
    rawInput = parse.getInputFromDict(inputDict)
    multiplier = 1

    for _ in range(repeatTimes):
        multiplier *= 2
        inputString = rawInput * multiplier
        sendBuffer.put(inputString)

# return dict of Nodes: node: [parents]
def findXMLNodes(root, nodes: dict = {}) -> dict:
    for child in root:
        nodes[child] = [root]
        nodes = findXMLNodes(child, nodes)
    return nodes

# return new nodes list with node and all its children removed
def removeNode(nodes: dict, node) -> dict:
    if node in nodes:
        nodes.pop(node)
    for child in node:
        nodes = removeNode(nodes, child)
    return nodes;

def sendXML(root):
    # remove prints after tested
    print('\n================\n')
    sys.stdout.buffer.write(ET.tostring(root))
    print('\n================\n')
    sendBuffer.put(ET.tostring(root))

Change = collections.namedtuple('Change', 'src dst parent')

def addChange(changesstack: List[Change], src, dst, nodes: dict, removeParent = False):
    if removeParent == False: # don't delete old parent - its a copy not a move
        changesstack.extend([Change(src, dst, None)])
        dst.append(src)
        nodes[src].append(dst)
    else:
        parent = nodes[src].pop()
        changesstack.extend([Change(src, dst, parent)])
        dst.append(src)
        nodes[src].append(dst)
        parent.remove(src)

def popChange(changesstack: List[Change], nodes: dict):
    change = changesstack.pop()
    change.dst.remove(change.src)
    nodes[change.src].pop()
    if change.parent is not None:
        change.parent.append(change.src)
        nodes[change.src].append(change.parent)

def popAllChanges(changesstack, nodes: dict):
    while changesstack != []:
        popChange(changesstack, nodes)

def mutationsXML(nodes: dict, root):
    changesstack = []
    
    i = 0
    while i < 100:
        src = random.choice(list(nodes))
        # move to be the child of any other valid node
        validDstNodes = list(removeNode(nodes.copy(), src))
        if validDstNodes == []:
            popChange(changesstack, nodes)
            # now what? continue but don't count this as an iteration
            continue

        dst = random.choice(validDstNodes)
        if random.randint(0, 1) == 0:
            addChange(changesstack, src, dst, nodes) # copy
        else:
            addChange(changesstack, src, dst, nodes, removeParent=True) # move
        sendXML(root)
        if random.randint(0, 4) == 0: # 25% chance to make new mutation, 75% chance to continue this one
            popAllChanges(changesstack, nodes)
        i += 1
    popAllChanges(changesstack, nodes)

def mutateXML(inputDict: dict):
    if inputDict.get('file') != FileType.XML:
        return
    logger.info('mutate XML')

    root = ET.ElementTree(ET.fromstring(parse.getInputFromDict(inputDict))).getroot()

    nodes = findXMLNodes(root)

    # choose a random node, move it to be child of another random node that isn't one of its children
    # the randomness is pointless because am trying all anyway and would need an insanely huge xml for that to take 3 mins
    for src in random.sample(nodes.keys(), len(nodes.keys())):
        # try with node removed
        nodes[src][-1].remove(src)
        sendXML(root)
        nodes[src][-1].append(src) # removing and adding back changes the order but w/e

        # move to be the child of any other valid node
        validDstNodes = list(removeNode(nodes.copy(), src))
        for dst in random.sample(validDstNodes, len(validDstNodes)):
            parent = nodes[src].pop()
            dst.append(src)
            nodes[src].append(dst) # set new parent
            parent.remove(src) # remove from old parent
            sendXML(root)
            mutationsXML(nodes, root)
            dst.remove(src)
            parent.append(src)
            nodes[src].remove(dst)
            nodes[src].append(parent)

def getMutations():
    return [mutateValues, mutateCSV, multiplyXML, multiplyJSON, invalidMultiplyInput, mutateXML, mutateBytes]

def emptyFile(inputDict: dict):
    sendBuffer.put(b'')
    sendBuffer.put(b'{}')
    sendBuffer.put(b'<>')
    sendBuffer.put(b',')
    sendBuffer.put(b' ')
    sendBuffer.put(b'{ }')
    sendBuffer.put(b'< >')
    sendBuffer.put(b', ')
    sendBuffer.put(b'\n'*100)
    sendBuffer.put(b',,,')

def getMutations():
    return [mutateValues, mutateCSV, multiplyXML, deepXML, multiplyJSON, longJSONList, invalidMultiplyInput, emptyFile, mutateBytes]
    
def setBuffers(_sendBuffer: Queue, _crashBuffer: Queue):
    global sendBuffer
    global crashBuffer
    sendBuffer = _sendBuffer
    crashBuffer = _crashBuffer