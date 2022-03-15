from os import path, mkdir, abort, rename

from utils.utils import getDataJSON
from .logger import error, info

DefaultConfig = {
    "prefix": "!",
    "plugins": [],
}

Config = {**DefaultConfig, **getDataJSON("config.json")}
BaseDir = path.join(path.dirname(__file__), "..")
DataDir = path.join(BaseDir, "data")

def prepare():
    if not path.exists(DataDir):
        mkdir(DataDir, 644)
    
    if not path.isdir(DataDir):
        error(f"Init Error: cannot init storage dir")
        abort()

def migrate():
    oldSession = path.join(BaseDir, "miaogram.session")
    newSession = path.join(DataDir, "miaogram.session")
    if path.exists(oldSession) and path.isfile(oldSession) and not path.exists(newSession):
        info("Init Migration: migrating session file")
        rename(oldSession, newSession)
