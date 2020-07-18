import parse
from pwn import *
from subprocess import *
import json

# hardcode these in a wordlists file
# research how to actually make a good fuzzer.
intcases = [-1, 0, 1, 10*(2**20), -10*(2**20)]
stringcases = ["A"*100, "\'", "\"", "\\", "#", "%", "--", " ", "\n", "`", ",", ".", "/", ""]
# "A"*1000, "A"*(2**30)
formatcases = ["%n"*10, "%s"*10, "%1000000$x"]
# "%x"*1000
# based on speed so far I estimate it will take more than one hour to run completely on csv

# We should have a function that makes strings of ever increasing length for overflow test

# global binary

# return inputWords dict that causes crash, or None if no crash
def permutations(inputWords: dict, i: int) -> dict:
    if i == len(inputWords['values']):
        return send(inputWords)
    else:
        testcases = [inputWords['values'][i]] # original value
        if isinstance(inputWords['values'][i], int):
            testcases += intcases
        elif isinstance(inputWords['values'][i], str):
            testcases += stringcases + formatcases
        else:
            raise()
        # float
        # other types?

        for case in testcases:
            inputWords['values'][i] = case
            res = permutations(inputWords, i+1)
            if res is not None:
                return res
        return None

# return True on segfault
def send(words: dict) -> bool:
    print("\n\n\n\n=============================================")
    # print(words)
    # print("\n\n\n\n=============================================")
    input = parse.getInputFromDict(words)

    print(input)
    p = subprocess.Popen(binary, stdin=PIPE)
    outs, errs = p.communicate(input.encode())
    print(outs)
    print(errs)

    if p.returncode != 0: # 139 for segfault
        print(p.returncode)
        return input

    return None

def generalFuzz(_binary: str, inputWords: dict) -> str:
    global binary 
    binary = _binary
    print(inputWords)
    crashInput = permutations(inputWords.copy(), 0)
    return crashInput
