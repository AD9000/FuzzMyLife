import parse
from subprocess import *
import json
import copy

from log import *

# put these in a wordlists file
intcases = [-1, 0, 1, 10*(2**30), -10*(2**30)]
stringcases = ["A"*10, "A"*100, "A"*1000, "\'", "\"", "\\", " ", "\n", "`", ",", "/", "", "\0"]
formatcases = ["%n"*10, "%n"*100, "%1000000$x"]
# allcases = intcases + stringcases + formatcases
allcases = [*intcases, *stringcases, *formatcases]

def fastFuzz(inputWords: dict) -> str:
    for i in range(len(inputWords['values'])):
        testcases = [inputWords['values'][i]] + allcases

        for case in testcases:
            payload = copy.deepcopy(inputWords)
            payload['values'][i] = case
            res = send(payload)
            if res is not None:
                return res

# return crashinput on segfault, else None
def send(words: dict) -> str:
    logger.debug("(separator below)\n\n\n\n=============================================")
    inputString = parse.getInputFromDict(words)

    p = Popen(binary, stdin=PIPE, stdout=PIPE)
    output, error = p.communicate(inputString.encode())
    logger.debug(output.decode())
    if (error):
        logger.error(error)

    if p.returncode == -11: # segfault code
        return inputString

    return None

def generalFuzz(_binary: str, inputWords: dict) -> str:
    global binary 
    binary = _binary
    crashInput = fastFuzz(inputWords.copy())
    return crashInput