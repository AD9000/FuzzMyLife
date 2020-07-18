import parse
from pwn import *
from subprocess import *
import json
import copy

# hardcode these in a wordlists file
# research how to actually make a good fuzzer.
intcases = [-1, 0, 1, 10*(2**20), -10*(2**20)]
stringcases = ["A"*1000, "\'", "\"", "\\", "#", "%", "--", " ", "\n", "`", ",", ".", "/", ""]
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

def fast_fuzz(inputWords: dict) -> dict:
    for i in range(len(inputWords['values'])):
        testcases = [inputWords['values'][i]]
        if isinstance(inputWords['values'][i], int):
            testcases += intcases
        elif isinstance(inputWords['values'][i], str):
            testcases += stringcases + formatcases
        else:
            raise()

        for case in testcases:
            payload = copy.deepcopy(inputWords)
            payload['values'][i] = case
            res = send(payload)
            if res is not None:
                return res

# return True on segfault
def send(words: dict) -> bool:
    print("\n\n\n\n=============================================")
    input = parse.getInputFromDict(words)

    p = subprocess.Popen(binary, stdin=PIPE)
    p.communicate(input.encode())

    if p.returncode != 0:
        return input

    return None

def generalFuzz(_binary: str, inputWords: dict) -> str:
    global binary 
    binary = _binary
    # crashInput = permutations(inputWords.copy(), 0)
    crashInput = fast_fuzz(inputWords.copy())
    return crashInput