import parse
import copy
from subprocess import *
from log import *

def mapFuzz(inputWords: dict):
    cases = ["A", 10]
    for i in inputWords:
        cases.append(inputWords[i])
        for j in cases:
            payload = copy.deepcopy(inputWords)
            payload[i] = j
            mapSend(payload)
        cases.remove(inputWords[i])

def isolateFields(inputWords: dict, output: str) -> list:
    keyIndexes = []
    cases = ["A", 10]
    for i in range(0, len(inputWords)):
        cases.append(inputWords[i])
        for j in cases:
            payload = copy.deepcopy(inputWords)
            payload[i] = j
            out = mapSend(payload)
            if out != output:
                keyIndexes.append(i)
                break
        cases.remove(inputWords[i])

    return keyIndexes

def mapSend(words: dict) -> str:
    inputString = parse.getInputFromDict(words)

    p = Popen(binary, stdin=PIPE, stdout=PIPE)
    output, error = p.communicate(inputString.encode())

    if output not in binmap:
        binmap[output] = isolateFields(words, output)
    return output

def mapper(_binary: str, inputWords: dict) -> str:
    global binary, binmap
    binmap = {}
    binary = _binary
    mapFuzz(inputWords)
    print(binmap)
    print(inputWords)