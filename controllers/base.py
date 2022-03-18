import glob
import sys
import re
import time
import schedule
from os import abort
from os.path import dirname, basename, isfile, join, exists
from typing import Callable, Dict, Union, List, Tuple
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.handlers import MessageHandler
from threading import Thread

from utils import app, logger, utils, config
from utils.config import getConfig, DataDir, currentVersionWithin

import importlib

PIPPARSER = re.compile('''^PIP\s*=\s*["']([\t a-zA-Z0-9_\-=<>!\.]+)["']\s*$''', re.M)
APKPARSER = re.compile('''^APK\s*=\s*["']([\t a-zA-Z0-9_\-=<>!\.]+)["']\s*$''', re.M)
async def scanPlugin(module: str) -> Dict[str, Dict[str, bool]]:
    result: Dict[str, Dict[str, bool]] = None
    path = config.fromBase(module.replace(".", "/") + ".py")
    file = utils.getTextFile(path)
    overall = True
    if file:
        result = {"apk": {}, "pip": {}, "overall": True}
        apks = APKPARSER.findall(file)
        if apks:
            packages: List[str] = apks[-1].strip().split()
            for package in packages:
                result["apk"][package] = await utils.apkInstall(package)
                logger.info(f'Register Service | external apk: {package} ({result["apk"][package]})')
                overall = overall and result["apk"][package]
        pips = PIPPARSER.findall(file)
        if pips:
            packages: List[str] = pips[-1].strip().split()
            for package in packages:
                result["pip"][package] = await utils.pipInstall(package)
                logger.info(f'Register Service | external pip: {package} ({result["pip"][package]})')
                overall = overall and result["pip"][package]
        result["overall"] = overall 
    return result

async def importPlugin(module, prefix="", level=0):
    moduleName = f"{prefix}{module}"
    await scanPlugin(moduleName)

    deregisterRelated(module, ["data.", "extra.", "controllers."])
    if moduleName in sys.modules:
        instance = importlib.reload(sys.modules[moduleName])
        logger.debug(f"Reloading module: {module} ({not not instance})")
        return instance

    instance = utils.importing(moduleName, level)
    logger.debug(f"Loading module: {module} ({not not instance})")
    return instance

async def reloadExternalPlugin(plugin) -> bool:
    prefix = "extra."
    if exists(join(DataDir, plugin+".py")):
        prefix = "data."
    
    if await importPlugin(plugin, prefix=prefix, level=0):
        return True
    else:
        return False

loadedPlugins = set()
async def reloadPlugins():
    global loadedPlugins
    
    # delete all jobs
    schedule.clear("p:miaogram")
    loadedPlugins.clear()

    folder = dirname(__file__)
    modules = [basename(f)[:-3] for f in glob.glob(join(folder, "*.py")) if isfile(f)]
    modules = list(set(modules))
    modules = [m for m in modules if not m.startswith(".") and not m.startswith("_") and m != "base"]
    success = []
    failure = []

    for module in modules:
        if await importPlugin(module, prefix="controllers.", level=0):
            success.append(module)
    
    plugins = list(set(getConfig("plugins", [])))
    for plugin in plugins:
        if await reloadExternalPlugin(plugin):
            success.append(plugin)
        else:
            failure.append(plugin)

    for p in success:
        loadedPlugins.add(p)
    return success, failure

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
    def __init__(self, module, fn, groupId, type, command, help, longHelp, handler, version):
        self.module = module
        self.groupId = groupId
        self.fn = fn
        self.help = help
        self.longHelp = longHelp
        self.handler = handler
        self.type = type
        self.command = command
        self.version = version

class Context:
    def __init__(self):
        pass
    
    def get(self, key: str) -> str:
        return config.readKey(key)

    def set(self, key: str, value: str):
        config.writeKeys([(key, value)])
    
    def sets(self, pairs: List[Tuple[str, str]]):
        config.writeKeys(pairs)

    def sql(self, query: str, *args, isMany) -> List[Tuple[str]]:
        try:
            return config.SQLRaw(query, *args, isMany=isMany).fetchall()
        except:
            return []

globalContext = Context()
groupNum = 0
pluginModules: Dict[str, Dict[str, ExtraModule]] = {}

def getFnName(func):
    return f"{func.__module__}.{func.__name__}"

def systemCheck(fnName, minVer=None, maxVer=None):
    if not currentVersionWithin(minVer, maxVer):
        logger.info(f"Register Service Error | version of {fnName} does not meet the requirement")
        return False
    return True

def deregisterModule(mi):
    if mi.type in ["command", "message"]:
        App.remove_handler(mi.handler, mi.groupId)
    elif mi.type in ["schedule"]:
        schedule.cancel_job(mi.handler)

def deregisterRelated(module, prefixes=[]):
    for prefix in prefixes:
        moduleName = f"{prefix}{module}"
        deregister(moduleName)

def deregister(moduleName):
    if moduleName in pluginModules:
        for functionName in pluginModules[moduleName]:
            logger.info(f"Register Service | unloading: {moduleName}.{functionName}")
            deregisterModule(pluginModules[moduleName][functionName])
        del pluginModules[moduleName]

def register(caller, original: Callable, type:str, command: str, help, longHelp, filters, version):
    global groupNum
    moduleName = original.__module__
    functionName = original.__name__
    if moduleName not in pluginModules:
        pluginModules[moduleName] = {}
    logger.info(f"Register Service | loading: {moduleName}.{functionName}")

    if functionName in pluginModules[moduleName]:
        deregisterModule(pluginModules[moduleName][functionName])
        del pluginModules[moduleName][functionName]
    if type in ["command", "message"]:
        handler = MessageHandler(caller, filters)
        pluginModules[moduleName][functionName] = ExtraModule(original.__module__, original.__name__, groupNum, type, command, help, longHelp, handler, version)
        App.add_handler(handler, groupNum)
        groupNum += 1
    elif type in ["schedule"]:
        pluginModules[moduleName][functionName] = ExtraModule(original.__module__, original.__name__, -1, type, command, help, longHelp, caller, version)

def onCommand(command="", help="", longHelp="", minVer=None, maxVer=None, filters=None, version="0.0.0") -> callable:
    def decorator(func: Callable) -> Callable:
        async def caller(client: Client, message: Message):
            if message and message.from_user and message.from_user.is_self and message.text:
                payloads = message.text.strip().split()
                if len(payloads) > 0 and payloads[0] == getConfig("prefix", "") + command:
                    logger.info(f"Calling plugin: {func.__module__}.{func.__name__} with={command} {payloads[1:]}")
                    args = Args(payloads[1:])
                    try:
                        await func(args, client, message, globalContext)
                    except Exception as e:
                        logger.error(f"Unexpected Error: {e}")
        if systemCheck(getFnName(func), minVer, maxVer):
            register(caller, func, "command", command, help or f"{command}", longHelp, filters, version)
        return caller
    return decorator

def onMessage(minVer=None, maxVer=None, filters=None, version="0.0.0") -> callable:
    def decorator(func: Callable) -> Callable:
        async def caller(client: Client, message: Message):
            try:
                await func(client, message, globalContext)
            except Exception as e:
                logger.error(f"Unexpected Error: {e}")
        if systemCheck(getFnName(func), minVer, maxVer):
            register(caller, func, "message", None, None, None, filters, version)
        return caller
    return decorator

every = schedule.every

def onSchedule(job: schedule.Job, minVer=None, maxVer=None, version="0.0.0", args=(), kargs={}) -> callable:
    def decorator(func: Callable) -> Callable:
        moduleTag = f"m:{func.__module__}"
        fnTag = getFnName(func)
        # clean old
        schedule.clear(moduleTag)

        # create a wrapper
        def wrapper(args, kargs):
            func(*args, **kargs)

        # register new
        if systemCheck(fnTag, minVer, maxVer):
            job.tag(moduleTag, "p:miaogram", f"f:{fnTag}").do(wrapper, args=args, kargs=kargs)
            register(job, func, "schedule", None, None, None, None, version)
        return func
    return decorator

schedulerRunning = False
def startScheduler():
    global schedulerRunning
    if schedulerRunning:
        return
    schedulerRunning = True

    def _runScheduler():
        while not app.Killed():
            try:
                schedule.run_pending()
            except Exception as e:
                logger.error(f"Scheduler Error | cannot finish jobs: {e}")
            time.sleep(1)

    x = Thread(target=_runScheduler)
    x.daemon = True
    x.start()
