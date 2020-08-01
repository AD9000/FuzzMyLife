import parse
from subprocess import *
import copy
# import gen_fuzz
import threaded_fuzz
from log import *

def addLines(inputWords: dict, j: int = 0) -> str:
    if (j > 3):
        return None
    
    logger.info("+++++++++++++++++++ j : {} +++++++++++++++".format(j))
    values = copy.deepcopy(inputWords['values'])

    inputWords['values'] = [*values, *values, *values]

    res = threaded_fuzz.threadedFuzz(binary, inputWords)
    if res is not None:
        logger.debug("RESFDSAGDSFADS")
        logger.debug(res)
        return res
    else:
        state = copy.deepcopy(inputWords)
        res = addCpl(state)
        if res is not None:
            return res
        return addLines(inputWords, j+1)
    

def addCpl(inputWords: dict) -> dict:
    values = inputWords['values']
    for i in range(1, len(values)):
        if len(values) % i == 0:
            inputWords['cpl'] = i - 1
            logger.debug(inputWords)
            res = threaded_fuzz.threadedFuzz(binary, inputWords)
            if res is not None:
                return res
    return None

def lineFuzz(_binary: str, inputWords: dict) -> str:
    if (inputWords['file'] != parse.FileType.CSV):
        return None

    global binary
    binary = _binary

    crashInput = addLines(copy.deepcopy(inputWords))
    return crashInput