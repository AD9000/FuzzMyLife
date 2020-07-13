import parse
from pwn import *

# hardcode these in a wordlists file
# research how to actually make a good fuzzer.
intcases = [-1, 0, 1, 10*(2**20), -10*(2**20)]
stringcases = ["A"*(2**10), "\'", "\"", "\\", "#", "%", "--", " ", "\n", "`", ",", ".", "/"]
formatcases = ["%x"*10000, "%n"*10000, "%s"*10000, "%p"*10000, "%1000000$x"]
# more As

# global binary

# return inputWords dict that causes crash, or None if no crash
def permutations(inputWords: dict, i: int) -> dict:
    if i == len(inputWords['values']):
        if send(inputWords):
            return inputWords
        return None
    else:
        if isinstance(inputWords['values'][i], int):
            testcases = intcases
        elif isinstance(inputWords['values'][i], str):
            testcases = stringcases + formatcases
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
    print(words)
    print("\n\n\n\n=============================================")
    input = parse.getInputFromDict(words)
    print("INPUT\n\n", input)
    p = process(binary)
    p.send(str(input))
    p.send(b"\x04") # EOT
    # wait until program is finished somehow
    exitCode = p.poll() # doesn't block
    if exitCode == 139: # segfault code, shouldn't hard code
        return True
    return False

def generalFuzz(_binary: str, inputWords: dict):
    global binary 
    binary = _binary
    print(inputWords)
    crashInput = permutations(inputWords.copy(), 0)
    if crashInput is not None:
        print('yahooooo')
        print(crashInput)
