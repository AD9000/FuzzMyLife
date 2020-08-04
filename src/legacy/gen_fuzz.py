import parse
from subprocess import *
import json
import copy

from log import *

# put into wordlist file?
intcases = [-1, 0, 1, 10*(2**20), -10*(2**20)]
stringcases = ["A"*10, "A"*100, "A"*1000, "\'", "\"", "\\", " ", "\n", "`", ",", "/", "", "\0"]
formatcases = ["%n"*10, "%n"*100, "%1000000$x"]

# specific cases for each file to try and break the format? or can parse do this instead?
# xmlCases?
# csvCases?
# jsonCases?

allcases = [*intcases, *stringcases, *formatcases]

def fastFuzz(inputWords: dict) -> str:
    for i in range(len(inputWords['values'])):
        testcases = [inputWords['values'][i]] + allcases

        for case in testcases:
            logger.info("creating payload")
            payload = copy.deepcopy(inputWords)
            payload['values'][i] = case
            logger.info("sending payload")
            res = send(payload)
            if res is not None:
                return res

# return crashinput on segfault, else None
def send(words: dict) -> str:
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
    crashInput = fastFuzz(copy.deepcopy(inputWords))
    return crashInput