import parse
from subprocess import *
import copy
import gen_fuzz
from log import *

def addLines(inputWords: dict, j: int = 0) -> str:
    if (j > 3):
        return None
    
    logger.info("+++++++++++++++++++ j : {} +++++++++++++++".format(j))
    values = copy.deepcopy(inputWords['values'])
    newVals = [*values, *values, *values]
    logger.info(newVals)

    inputWords['values'] = newVals

    res = gen_fuzz.fastFuzz(inputWords)
    if res is not None:
        logger.debug("RESFDSAGDSFADS")
        logger.debug("====================")
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
            res = gen_fuzz.fastFuzz(inputWords)
            if res is not None:
                return res
    return None

def lineFuzz(_binary: str, inputWords: dict) -> str:
    gen_fuzz.binary = _binary
    if (inputWords['file'] != parse.FileType.CSV):
        return None
    crashInput = addLines(copy.deepcopy(inputWords))
    return crashInput