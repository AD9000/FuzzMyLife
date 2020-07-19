import parse
from subprocess import *
import json
import copy

from log import *

# put these in a wordlists file
intcases = [-1, 0, 1, 10*(2**20), -10*(2**20)]
stringcases = ["A"*10, "A"*100, "A"*1000, "\'", "\"", "\\", "#", "%", "--", " ", "\n", "`", ",", ".", "/", ""]
formatcases = ["%n"*10, "%n"*100, "%1000000$x"]
allcases = intcases + stringcases + formatcases

# did you mean fastFuzz
# you demon
def fast_fuzz(inputWords: dict) -> str:
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

    if p.returncode != 0:
        return inputString

    return None

def generalFuzz(_binary: str, inputWords: dict) -> str:
    global binary 
    binary = _binary
    crashInput = fast_fuzz(inputWords.copy())
    return crashInput