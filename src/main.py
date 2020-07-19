#!/usr/bin/python3
import sys
import os

import parse
import gen_fuzz
import line_fuzz
from log import *

'''
Show the input that crashed the program returned from the fuzzers
'''
def handleCrash(crashInput):
    if crashInput is not None:
        logger.info("Found crash")
        logger.info(crashInput)
        with open(ROOT_DIR + "bad.txt", "w") as badtxt:
            badtxt.write(crashInput)
        logger.info('\n\nBad input written to ' + os.path.join(ROOT_DIR, 'bad.txt'))
        return True
    return False

'''
Cleanup, logging before exit
'''
def exitSafely(code=0):
    logger.info('Done')
    exit(0)

'''
Check that user has passed in args properly, otherwise print usage
'''
def checkArgs():
    if len(sys.argv) != 3:
        logger.info(f"Usage: {sys.argv[0]} binaryfilename inputfilename")
        exitSafely()

'''
Runs the line fuzzer from line_fuzz
'''
def runLineFuzzer(binary, inputDict):
    logger.debug('starting line fuzzer...')
    
    # running the line fuzzer, that mutates the amount of input
    crashInput = line_fuzz.lineFuzz(binary, inputDict)
    logger.debug('finished running line fuzzer')

    # Check if there was a crash
    if handleCrash(crashInput):
        exitSafely()

'''
Runs the general fuzzer from gen_fuzz
'''
def runGeneralFuzzer(binary, inputDict):
    logger.debug('starting general fuzzer...')

    # running the general fuzzer, mutates input values
    crashInput = gen_fuzz.generalFuzz(binary, inputDict)
    logger.debug('finished running general fuzzer')

    # Check if there was a crash
    if handleCrash(crashInput):
        exitSafely()

if __name__ == "__main__":
    checkArgs()

    # extract args
    binary = sys.argv[1]
    inputFileName = sys.argv[2]

    # logs for sanity
    logger.debug(binary)
    logger.debug(inputFileName)
    logger.info('Starting fuzzer...')

    # parse input into an array for the fuzzer
    inputDict = parse.getDictFromInput(inputFileName)
    
    runLineFuzzer(binary, inputDict)
    runGeneralFuzzer(binary, inputDict)
    
    # all fuzzers failed
    logger.info(":'(")
    logger.info('done')

        