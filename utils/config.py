import json
import sqlite3

from os import path, mkdir, abort, rename
from .utils import existDataFile, existExtraFile, getDataJSON, importing, setDataFile, toInt, BaseDir, DataDir
from .logger import error, info
from typing import Tuple, List

VERSION = "1.3.0"

DefaultConfig = {
    "prefix": "!",
    "plugins": [],
}

Config = {**DefaultConfig}
SQLiteInstance: sqlite3.Connection = None

def fromBase(p: str=""):
    return path.join(BaseDir, p)

def getConfig(path: str="", default=None):
    cfg = Config
    for p in path.split("."):
        try:
            cfg = cfg[p]
        except:
            return default
    return cfg

def addPluginWhiteList(pluginName: str) -> bool:
    if pluginName in Config["plugins"]:
        return True
    if not existDataFile(f"{pluginName}.py") and not existExtraFile(f"{pluginName}.py"):
        return False
    Config["plugins"].append(pluginName)
    setDataFile("config.json", json.dumps(Config, indent=2))
    return True

def delPluginWhiteList(pluginName: str) -> bool:
    if pluginName not in Config["plugins"]:
        return True
    Config["plugins"].remove(pluginName)
    setDataFile("config.json", json.dumps(Config, indent=2))
    return True

def reloadConfig():
    global Config
    Config = {**DefaultConfig, **getDataJSON("config.json")}

def prepare():
    # prepare data
    if not path.exists(DataDir):
        mkdir(DataDir, 644)
    
    if not path.isdir(DataDir):
        error(f"Init Error: cannot init storage dir")
        abort()
    
    # prepare sql
    global SQLiteInstance
    SQLiteInstance = sqlite3.connect(path.join(DataDir, 'miaogram.store'))

    cur = SQLiteInstance.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS kv (k VARCHAR(128) PRIMARY KEY, v TEXT)''')
    SQLiteInstance.commit()

    # prepare preload
    importing('data.__preload__') or importing('extra.__preload__')

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

def SQLRaw(sql, iterables, isMany=False) -> sqlite3.Cursor:
    try:
        cur = SQLiteInstance.cursor()
        result = None
        if not isMany:
            result = cur.execute(sql, iterables)
        else:
            result = cur.executemany(sql, iterables)
        SQLiteInstance.commit()

        return result
    except Exception as e:
        error(f"SQL Exec Error: cannot run query {sql} {iterables}: {e}")
        return None

def readKey(key: str) -> str:
    try:
        ret = SQLRaw('''SELECT k, v FROM kv WHERE k = ?''', (key,)).fetchall()
        if ret and len(ret[0]) >= 2:
            return ret[0][1]
    except:
        pass
    return ''

def writeKeys(pairs: List[Tuple[str, str]]):
    try:
        SQLRaw('''REPLACE INTO `kv` (k, v) VALUES (?, ?)''', pairs, isMany=True)
    except:
        pass

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
