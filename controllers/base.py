import glob
import sys
from os import abort
from os.path import dirname, basename, isfile, join, exists
from typing import Callable, Dict, Union
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.handlers import MessageHandler

from utils import app, logger, utils
from utils.config import getConfig, DataDir, currentVersionWithin

import importlib

def importPlugin(module, prefix="", level=0):
    moduleName = f"{prefix}{module}"
    if moduleName in sys.modules:
        instance = importlib.reload(sys.modules[moduleName])
        logger.debug(f"Reloading module: {module} ({not not instance})")
        return instance

    instance = utils.tryf(lambda: __import__(moduleName, globals(), locals(), level=level))
    logger.debug(f"Loading module: {module} ({not not instance})")
    return instance

def reloadPlugins():
    folder = dirname(__file__)
    modules = [basename(f)[:-3] for f in glob.glob(join(folder, "*.py")) if isfile(f)]
    modules = list(set(modules))
    modules = [m for m in modules if not m.startswith(".") and not m.startswith("_") and m != "base"]
    success = []

    for module in modules:
        if importPlugin(module, prefix="controllers.", level=0):
            success.append(module)
    
    plugins = list(set(getConfig("plugins", [])))
    for plugin in plugins:
        if exists(join(DataDir, plugin+".py")):
            if importPlugin(plugin, prefix="data.", level=0):
                success.append(plugin)
        else:
            if importPlugin(plugin, prefix="extra.", level=0):
                success.append(plugin)

    return success

if app.App == None:
    logger.error("Cannot call controller init before app is defined.")
    abort()

App = app.App

class Args(list):
    def getAll(self) -> str:
        return " ".join(self).strip()

    def get(self, index: int) -> Union[str, None]:
        if len(self) > index:
            return self[index]
        return None
    
    def getInt(self, index: int) -> int:
        return utils.toInt(self.get(index))


class ExtraModule:
    def __init__(self, module, fn, groupId, command, help, longHelp, handler):
        self.module = module
        self.groupId = groupId
        self.fn = fn
        self.help = help
        self.longHelp = longHelp
        self.handler = handler
        self.command = command

groupNum = 0
modules: Dict[str, ExtraModule] = {}

def getFnName(func):
    return f"{func.__module__}.{func.__name__}"

def systemCheck(fnName, minVer=None, maxVer=None):
    if not currentVersionWithin(minVer, maxVer):
        logger.info(f"Register Service Error | version of {fnName} does not meet the requirement")
        return False
    return True

def register(caller, original: Callable, command: str, help, longHelp, filters):
    global groupNum
    fnName = getFnName(original)
    if fnName in modules:
        logger.info(f"Register Service | reloading: {fnName}")
        App.remove_handler(modules[fnName].handler, modules[fnName].groupId)
    else:
        logger.info(f"Register Service | loading: {fnName}")
    handler = MessageHandler(caller, filters)
    modules[fnName] = ExtraModule(original.__module__, original.__name__, groupNum, command, help, longHelp, handler)
    App.add_handler(handler, groupNum)
    groupNum += 1

def onCommand(command="", help="", longHelp="", minVer=None, maxVer=None, filters=None) -> callable:
    def decorator(func: Callable) -> Callable:
        async def caller(client: Client, message: Message):
            if message and message.from_user and message.from_user.is_self and message.text:
                payloads = message.text.strip().split()
                if len(payloads) > 0 and payloads[0] == getConfig("prefix", "") + command:
                    logger.info(f"Calling plugin: {command} with={payloads[1:]}")
                    args = Args(payloads[1:])
                    try:
                        await func(args, client, message)
                    except Exception as e:
                        logger.error(f"Unexpected Error: {e}")
        if systemCheck(getFnName(func), minVer, maxVer):
            register(caller, func, command, help or f"{command}", longHelp, filters)
        return caller
    return decorator

def onMessage(minVer=None, maxVer=None, filters=None) -> callable:
    def decorator(func: Callable) -> Callable:
        async def caller(client: Client, message: Message):
            try:
                await func(client, message)
            except Exception as e:
                logger.error(f"Unexpected Error: {e}")
        if systemCheck(getFnName(func), minVer, maxVer):
            register(caller, func, None, None, None, filters)
        return caller
    return decorator