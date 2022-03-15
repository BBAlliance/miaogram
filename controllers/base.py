import glob
import sys
from os import abort
from os.path import dirname, basename, isfile, join, exists
from typing import Callable, Dict, Union
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.handlers import MessageHandler

from utils import app, logger, utils
from utils.config import Config, DataDir

import importlib

def importPlugin(module, prefix="", level=0):
    moduleName = f"{prefix}{module}"
    if moduleName in sys.modules:
        instance = importlib.reload(sys.modules[moduleName])
        logger.info(f"Reloading module: {module} ({not not instance})")
        return instance

    instance = utils.tryf(lambda: __import__(moduleName, globals(), locals(), level=level))
    logger.info(f"Loading module: {module} ({not not instance})")
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

    for plugin in Config["plugins"]:
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
    def __init__(self, module, fn, groupId, help, handler):
        self.module = module
        self.groupId = groupId
        self.fn = fn
        self.help = help
        self.handler = handler

groupNum = 0
modules: Dict[str, ExtraModule] = {}

def register(caller, original: Callable, help, filters):
    global groupNum
    fnName = f"{original.__module__}.{original.__name__}"
    if fnName in modules:
        logger.info(f"Register Service | replacing: {fnName}")
        App.remove_handler(modules[fnName].handler, modules[fnName].groupId)
    handler = MessageHandler(caller, filters)
    modules[fnName] = ExtraModule(original.__module__, original.__name__, groupNum, help, handler)
    App.add_handler(handler, groupNum)
    groupNum += 1

def onCommand(command="", help="", filters=None) -> callable:
    def decorator(func: Callable) -> Callable:
        async def caller(client: Client, message: Message):
            if message and message.from_user and message.from_user.is_self and message.text:
                payloads = message.text.strip().split()
                if len(payloads) > 0 and payloads[0] == Config["prefix"] + command:
                    logger.info(f"Calling plugin: {command} with={payloads[1:]}")
                    args = Args(payloads[1:])
                    try:
                        await func(args, client, message)
                    except Exception as e:
                        logger.error(f"Unexpected Error: {e}")
        register(caller, func, help or f"{command}", filters)
        return caller
    return decorator

def onMessage(filters=None) -> callable:
    def decorator(func: Callable) -> Callable:
        async def caller(client: Client, message: Message):
            try:
                await func(client, message)
            except Exception as e:
                logger.error(f"Unexpected Error: {e}")
        register(caller, func, None, filters)
        return caller
    return decorator