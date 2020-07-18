import sys

import parse
import gen_fuzz

# The only real requirement is that you supply an executable file that takes in a single argument (the binary to fuzz),
# your executable should create a file called bad.txt which if passed into the binary as input causes the program to crash.

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} binaryfilename inputfilename")
        exit()
    binary = sys.argv[1]
    inputFileName = sys.argv[2]
    print(binary)
    print(inputFileName)

    # parse
    inputDict = parse.getDictFromInput(inputFileName)
    # fuzz
    crashInput = gen_fuzz.generalFuzz(binary, inputDict)
    if crashInput is not None:
        print("Found crash")
        print(crashInput)
        with open("bad.txt", "w") as f:
            f.write(crashInput)
    else:
        print(":'(")
        