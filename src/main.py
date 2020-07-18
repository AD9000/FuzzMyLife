import sys

import parse
import gen_fuzz

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
    gen_fuzz.generalFuzz(binary, inputDict)
