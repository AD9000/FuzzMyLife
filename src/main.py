import sys

import parse
import gen_fuzz

if __name__ == "__main__":
    binary = sys.argv[1]
    inputFileName = sys.argv[2]
    print(binary)
    print(inputFileName)

    # parse
    inputDict = parse.getDictFromInput(inputFileName)
    gen_fuzz.generalFuzz(binary, inputDict)
