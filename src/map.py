import parse
import copy
from subprocess import *
from log import *
import thread_manager

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
            out,error = thread_manager.sendWithOutput(newWords, binary)
            if out != output:
                keyIndexes.append({i: inputWords["values"][i]})
                break
        cases.remove(inputWords["values"][i])
    
    return keyIndexes

def mapSend(words: dict) -> str:
    inputString = parse.getInputFromDict(words)
    output, error = thread_manager.sendWithOutput(words, binary)
    
    if output not in binMap:
        binMap[output] = isolateFields(words, output)

    return output

def mapper(_binary: str, inputWords: dict) -> str:
    global binary, binMap
    binMap = {}
    binary = _binary
    mapFuzz(inputWords)
    return binMap