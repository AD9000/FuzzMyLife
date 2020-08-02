import parse
import copy
from subprocess import *
from log import *

def mapFuzz(inputWords: dict):
    cases = ["A", 10]
    newWords = copy.deepcopy(inputWords)
    for i in range (0, len(inputWords["values"])):
        cases.append(inputWords["values"][i])
        for j in cases:
            payload = copy.deepcopy(inputWords["values"])
            payload[i] = j
            newWords["values"] = payload
            mapSend(newWords)
        cases.remove(inputWords["values"][i])

def isolateFields(inputWords: dict, output: str) -> list:
    keyIndexes = []
    cases = ["A", 10]
    newWords = copy.deepcopy(inputWords)

    for i in range(0, len(inputWords["values"])):
        cases.append(inputWords["values"][i])
        for j in cases:
            payload = copy.deepcopy(inputWords["values"])
            payload[i] = j
            newWords["values"] = payload
            out = outSend(newWords)
            if out != output:
                keyIndexes.append({i: inputWords["values"][i]})
                break
        cases.remove(inputWords["values"][i])
    
    return keyIndexes

def mapSend(words: dict) -> str:
    inputString = parse.getInputFromDict(words)

    p = Popen(binary, stdin=PIPE, stdout=PIPE)
    output, error = p.communicate(inputString.encode())
    
    if output not in binmap:
        binmap[output] = isolateFields(words, output)

    return output

def outSend(words: dict) -> str:
    inputString = parse.getInputFromDict(words)

    p = Popen(binary, stdin=PIPE, stdout=PIPE)
    output, error = p.communicate(inputString.encode())
    
    return output

def mapper(_binary: str, inputWords: dict) -> str:
    global binary, binmap
    binmap = {}
    binary = _binary
    mapFuzz(inputWords)
    for i in binmap:
        print(str(i) + ": " + str(binmap[i]))