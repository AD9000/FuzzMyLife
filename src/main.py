#!/usr/bin/python3
import sys
import os

import parse
import gen_fuzz
import line_fuzz
from log import *

# The only real requirement is that you supply an executable file that takes in a single argument (the binary to fuzz),
# Creates a file called bad.txt which if passed into the binary as input causes the program to crash.

def handleCrash(crashInput):
    if crashInput is not None:
        logger.info("Found crash")
        logger.info(crashInput)
        with open(ROOT_DIR + "bad.txt", "w") as badtxt:
            badtxt.write(crashInput)
        logger.info('\n\nBad input written to ' + os.path.join(ROOT_DIR, 'bad.txt'))
        return True
    return False

def exitSafely(code=0):
    logger.info('Done')
    exit(0)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        logger.info(f"Usage: {sys.argv[0]} binaryfilename inputfilename")
        exit()
    binary = sys.argv[1]
    inputFileName = sys.argv[2]
    logger.debug(binary)
    logger.debug(inputFileName)
    logger.info('Starting fuzzer...')

    # parse
    inputDict = parse.getDictFromInput(inputFileName)

    logger.debug('starting line fuzzer...')
    # fuzz
    crashInput = line_fuzz.lineFuzz(binary, inputDict)
    logger.debug('finished running line fuzzer')
    if handleCrash(crashInput):
        exitSafely()

    logger.debug('starting general fuzzer...')
    crashInput = gen_fuzz.generalFuzz(binary, inputDict)
    logger.debug('finished running general fuzzer')
    if handleCrash(crashInput):
        exitSafely()
    else:
        logger.info(":'(")

    logger.info('done')

        