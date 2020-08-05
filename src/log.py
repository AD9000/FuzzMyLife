import sys
import logging
import os
from pathlib import Path

# Paths to different directories

def getSimpleLogger(logfile='log.txt'):
    global ROOT_DIR
    global LOG_DIR
    global LOG_PATH
    global CRASH_DIR
    global logger

    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    LOG_DIR = os.path.join(ROOT_DIR, 'logs')
    LOG_PATH = os.path.join(LOG_DIR, logfile)
    CRASH_DIR = LOG_DIR

    # Create logger if does not exist
    Path(LOG_DIR).mkdir(parents=True, exist_ok=True)

    # Create logger that logs everything
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Logger writes to a file named log.txt
    fileFormatter = logging.Formatter("%(asctime)s [%(threadName)s] [%(levelname)s]: %(message)s")
    fileHandler = logging.FileHandler(LOG_PATH)
    fileHandler.setFormatter(fileFormatter)
    logger.addHandler(fileHandler)

    # Logger also writes to stdout
    consoleFormatter = logging.Formatter("%(message)s")
    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setLevel(logging.DEBUG)
    consoleHandler.setFormatter(consoleFormatter)
    logger.addHandler(consoleHandler)

def getSubmissionLogger():
    global ROOT_DIR
    global LOG_DIR
    global LOG_PATH
    global CRASH_DIR
    global logger

    # Temporarily use the src/ folder
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    LOG_DIR = os.path.join(ROOT_DIR, 'logs')
    LOG_PATH = os.path.join(LOG_DIR, 'log.txt')
    CRASH_DIR = ROOT_DIR

    # Create logger if does not exist
    Path(LOG_DIR).mkdir(parents=True, exist_ok=True)

    # Create logger that logs everything
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Logger also writes to stdout
    consoleFormatter = logging.Formatter("%(message)s")
    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setLevel(logging.INFO)
    consoleHandler.setFormatter(consoleFormatter)
    logger.addHandler(consoleHandler)


if '-d' in sys.argv:
    logfile = 'log.txt'
    if '--logfile' in sys.argv:
        index = sys.argv.index('--logfile')
        logfile = sys.argv[index + 1]
    
    getSimpleLogger(logfile)
else:
    getSubmissionLogger()

