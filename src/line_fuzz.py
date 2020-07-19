import parse
from subprocess import *
import copy
import gen_fuzz
from log import *

limit_checkr = 0

def addLines(inputWords: dict) -> str:
    global limit_checkr
    limit_checkr += 1
    if (limit_checkr > 8):
        return None
    
    values = copy.deepcopy(inputWords['values'])
    for i in inputWords['values']:
        values.append(i)
    inputWords['values'] = values
    res = gen_fuzz.fast_fuzz(inputWords)
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
        return addLines(inputWords)
        
    

def addCpl(inputWords: dict) -> dict:
    values = inputWords['values']
    for i in range(1, len(values)):
        if len(values) % i == 0:
            inputWords['cpl'] = i - 1
            logger.debug(inputWords)
            res = gen_fuzz.fast_fuzz(inputWords)
            if res is not None:
                return res
    return None

def lineFuzz(_binary: str, inputWords: dict) -> str:
    gen_fuzz.binary = _binary
    if (inputWords['file'] != parse.FileType.CSV):
        return None
    crashInput = addLines(inputWords)
    return crashInput