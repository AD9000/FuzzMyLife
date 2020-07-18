import parse
from subprocess import *
import copy

limit_check = 0

def addLines(inputWords: dict) -> dict:
    global limit_check
    limit_check += 1
    if (limit_check > 50):
        return None
    
    values = copy.deepcopy(inputWords['values'])
    for i in inputWords['values']:
        values.append(i)
    inputWords['values'] = values
    
    res = send(inputWords)
    if res is not None:
        return res
    else:
        addLines(inputWords)


# return True on segfault
def send(words: dict) -> bool:
    print("\n\n\n\n=============================================")
    # print(words)
    # print("\n\n\n\n=============================================")
    input = parse.getInputFromDict(words)

    print(input)
    p = Popen(binary, stdin=PIPE)
    outs, errs = p.communicate(input.encode())
    print(outs)
    print(errs)

    if p.returncode != 0: # 139 for segfault
        print(p.returncode)
        return input

    return None

def lineFuzz(_binary: str, inputWords: dict) -> str:
    #This can only currenrtly be done with csv 
    global binary 
    binary = _binary
    if (inputWords['file'] != parse.FileType.CSV):
        return None
    print(inputWords)
    crashInput = addLines(inputWords.copy())
    return crashInput