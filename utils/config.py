import json
from os import path, mkdir, abort, rename

from utils.utils import existDataFile, getDataJSON, setDataFile, toInt, tryf
from .logger import error, info

VERSION = "1.0.0"

DefaultConfig = {
    "prefix": "!",
    "plugins": [],
}

Config = {**DefaultConfig}
BaseDir = path.join(path.dirname(__file__), "..")
DataDir = path.join(BaseDir, "data")

def getConfig(path: str="", default=None):
    cfg = Config
    for p in path.split("."):
        try:
            cfg = cfg[p]
        except:
            return default
    return cfg

def reloadConfig():
    global Config
    Config = {**DefaultConfig, **getDataJSON("config.json")}

def prepare():
    if not path.exists(DataDir):
        mkdir(DataDir, 644)
    
    if not path.isdir(DataDir):
        error(f"Init Error: cannot init storage dir")
        abort()

def migrate():
    # session migration, deprecated 1.0.0
    oldSession = path.join(BaseDir, "miaogram.session")
    newSession = path.join(DataDir, "miaogram.session")
    if path.exists(oldSession) and path.isfile(oldSession) and not path.exists(newSession):
        info("Init Migration: migrating session file")
        rename(oldSession, newSession)
    
    # init config.plugin
    if not existDataFile("config.json"):
        info("Init Migration: migrating initial plugins")
        Config["plugins"] = ["dme", "google", "ping", "re", "speedtest", "pic", "diss"]
        setDataFile("config.json", json.dumps(Config, indent=2))

def encodeVersion(v=''):
    vs = v.split(".") + ['0'] * 3
    factor = 1000 * 1000
    result = 0
    for i in range(3):
        result += toInt(vs[i]) * factor
        factor /= 1000
    return int(result)

def compareVersion(v):
    my = encodeVersion(VERSION)
    v0 = encodeVersion(v)
    if my == v0:
        return 0
    elif v0 < my:
        return -1
    else:
        return 1

def currentVersionWithin(min=None, max=None):
    if min == None and max == None:
        return True
    if isinstance(min, str) and compareVersion(min) > 0:
        return False
    if isinstance(max, str) and compareVersion(max) < 0:
        return False
    if not isinstance(min, str) and not isinstance(max, str):
        return False
    return True
