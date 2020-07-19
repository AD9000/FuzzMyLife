import sys
import logging
import os
from pathlib import Path

# Paths to different directories
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(ROOT_DIR, 'logs')
LOG_PATH = os.path.join(LOG_DIR, 'log.txt')

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
consoleHandler.setLevel(logging.INFO)
consoleHandler.setFormatter(consoleFormatter)
logger.addHandler(consoleHandler)