from enum import Enum, auto

class FileType(Enum):
    PLAINTEXT = auto()
    CSV = auto()
    JSON = auto()
    XML = auto()
    NONE = auto()