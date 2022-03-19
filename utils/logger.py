import time

from utils.utils import TempDir
from os.path import join
from os import environ

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

LogBank = []
def prepareLogBank():
    global LogFile, FileAdapter
    if "LOGFILE" in environ:
        FileAdapter = environ["LOGFILE"]
    if FileAdapter:
        try:
            LogFile = open(join(TempDir, FileAdapter), "a")
        except:
            pass

def getLogBank(lines):
    global LogBank
    return LogBank[-lines:]

def writeLogBank(data):
    global LogBank, LogFile
    if len(LogBank) > 500:
        LogBank = LogBank[250:]
    if type(data) != type(""):
        try:
            data = str(data, encoding='utf-8')
        except:
            data = f"Undecodable Data: {data}"
            pass
    
    if not data:
        return
    
    try:
        if LogFile:
            LogFile.write(data)
            LogFile.flush()
    except:
        pass
    LogBank.append(data)

class HijeckedBuffer(object):
   def __init__(self, stream):
       self.stream = stream
   def write(self, data):
       self.stream.write(data)
       writeLogBank(data)
   def writelines(self, datas):
       self.stream.writelines(datas)
       writeLogBank(datas)
   def __getattr__(self, attr):
       return getattr(self.stream, attr)

def hijack():
    import sys
    sys.stdout = HijeckedBuffer(sys.stdout)
    sys.stderr = HijeckedBuffer(sys.stderr)

def logger(level=INFO, msg=""):
    if level >= VerboseLevel:
        p = Prefixes[level]
        t = time.strftime("%a %b %d %H:%M:%S %Y", time.localtime())
        print(f"{p} | {t} | {msg}\n", end="")

def error(info: str):
    logger(ERROR, info)

def warn(info: str):
    logger(WARN, info)

def info(info: str):
    logger(INFO, info)

def debug(info: str):
    logger(DEBUG, info)
