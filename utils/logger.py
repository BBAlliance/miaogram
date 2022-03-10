import time

ERROR = 40
WARN = 30
INFO = 20
DEBUG = 10

Prefixes = {
    ERROR: "ERRO",
    WARN: "WARN",
    INFO: "INFO",
    DEBUG: "DEBG",
}

VerboseLevel = INFO
FileAdapter = ""

def logger(level=INFO, *msg):
    if level >= VerboseLevel:
        print(Prefixes[level], time.strftime("%a %b %d %H:%M:%S %Y", time.localtime()), *msg, sep=" | ")

    if FileAdapter:
        #TODO file adapter
        pass

def error(info: str):
    logger(ERROR, info)

def warn(info: str):
    logger(WARN, info)

def info(info: str):
    logger(INFO, info)

def debug(info: str):
    logger(DEBUG, info)
