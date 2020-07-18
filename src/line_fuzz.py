import parse
from subprocess import *
import copy

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
    res = send(inputWords)
    if res is not None:
        print("RESFDSAGDSFADS")
        print("====================")
        print(res)
        return res
    else:
        # state = copy.deepcopy(inputWords)
        # res = addCpl(state)
        # if res is not None:
        #     return res
        # else:
        addLines(inputWords)

def addCpl(inputWords: dict) -> dict:
    values = inputWords['values']
    for i in range(1, len(values)):
        if len(values) % i == 0:
            inputWords['cpl'] = i
            print(inputWords)
            res = send(inputWords)
            if res is not None:
                return res
    return None

# return True on segfault
def send(words: dict) -> str:
    print("\n\n\n\n=============================================")
    input = parse.getInputFromDict(words)

    p = Popen(binary, stdin=PIPE)
    p.communicate(input.encode())

    if p.returncode != 0:
        print(p.returncode)
        return input
    return None

def lineFuzz(_binary: str, inputWords: dict) -> str:
    global binary 
    binary = _binary
    if (inputWords['file'] != parse.FileType.CSV):
        return None
    crashInput = addLines(inputWords)
    print("crash input is: " + str(crashInput))
    return crashInput