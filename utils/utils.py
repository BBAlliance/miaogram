import sys

from asyncio import create_subprocess_shell, sleep
from asyncio.subprocess import PIPE
from typing import List, Dict, Union
from random import randint
from os import path, unlink
from threading import Thread
from glob import glob
from .logger import error

import json

BaseDir = path.join(path.dirname(__file__), "..")
DataDir = path.join(BaseDir, "data")

def toInt(s) -> int:
    try:
        return int(s)
    except Exception:
        return 0

def rand():
    return randint(0, 65535)

def randPick(lib: List):
    return lib[randint(0, len(lib)-1)]

def randStr():
    i = rand()
    return f"{i}"

async def threadingExec(prog, args=()):
    x = Thread(target=prog, args=args)
    x.start()

    interval = 0.01
    await sleep(interval)

    while x.is_alive():
        await sleep(interval)

async def execute(command, outputError=True):
    executor = await create_subprocess_shell(
        command,
        stdout=PIPE,
        stderr=PIPE
    )

    try:
        stdout, stderr = await executor.communicate()
    except:
        return "发生错误"
    if outputError:
        result = str(stdout.decode().strip()) \
                 + str(stderr.decode().strip())
    else:
        result = str(stdout.decode().strip())
    return result

async def bash(file, outputError=True):
    return await execute("/bin/bash " + path.join(path.dirname(__file__), "..", file), outputError)

def convertBits(bits):
    power = 1024
    zero = 0
    units = {
        0: '',
        1: 'Kbps',
        2: 'Mbps',
        3: 'Gbps',
        4: 'Tbps'}
    while bits > power:
        bits /= power
        zero += 1
    return f"{round(bits, 2)} {units[zero]}"

def convertBytes(bits):
    bits /= 8
    power = 1024
    zero = 0
    units = {
        0: '',
        1: 'KB/s',
        2: 'MB/s',
        3: 'GB/s',
        4: 'TB/s'}
    while bits > power:
        bits /= power
        zero += 1
    return f"{round(bits, 2)} {units[zero]}"

def getTextFile(file: str) -> str:
    content = ""
    try:
        with open(file, "r") as f:
            content = f.read()
    except:
        pass
    return content

def writeTextFile(file: str, content: str):
    try:
        with open(file, "w") as f:
            f.write(content)
        return True
    except:
        pass
    return False

def getVendor(file: str):
    return getTextFile(path.join(path.dirname(__file__), "../vendors", file))
    
def getDataFile(file: str):
    return getTextFile(path.join(path.dirname(__file__), "../data", file))

def getExtraFile(file: str):
    return getTextFile(path.join(path.dirname(__file__), "../extra", file))

def setDataFile(file: str, content: str):
    return writeTextFile(path.join(path.dirname(__file__), "../data", file), content)

def delDataFile(file: str):
    tryf(lambda: unlink(path.join(path.dirname(__file__), "../data", file)))

def existDataFile(file: str):
    return path.exists(path.join(path.dirname(__file__), "../data", file))

def existExtraFile(file: str):
    return path.exists(path.join(path.dirname(__file__), "../extra", file))

def listFiles(pattern: str = ""):
    return [f for f in glob(path.join(BaseDir, pattern)) if path.isfile(f)]

def getDataJSON(file: str) -> Dict:
    try:
        return json.loads(getDataFile(file))
    except:
        return {}

def removeExt(file: str) -> str:
    if not isinstance(file, str):
        return ""
    return ".".join(file.split(".")[:-1]) or file

def tryf(fn, verbose=False):
    try:
        return fn()
    except Exception as e:
        if verbose:
            print(f"Trying Error | cannot accomplish goal: {e}")

def importing(absolutePath, level=0):
    return tryf(lambda: __import__(absolutePath, globals(), locals(), level=level), True)

async def pipInstall(packages: Union[str, List[str]]) -> bool:
    if isinstance(packages, list):
        packages = ' '.join(packages)
    executor = await create_subprocess_shell(
        ' '.join([sys.executable, "-m", "pip", "install", packages]),
        stdout=PIPE,
        stderr=PIPE
    )

    try:
        stdout, stderr = await executor.communicate()
    except:
        return False

    stdout = stdout.decode().strip()
    stderr = stderr.decode().strip()
    if stderr and not executor.returncode:
        error(f"Pip Installer Error: {executor.returncode}: {stderr}")
    
    if executor.returncode == 0:
        return True
    return False

async def apkInstall(packages: Union[str, List[str]]) -> bool:
    if isinstance(packages, list):
        packages = ' '.join(packages)
    executor = await create_subprocess_shell(
        ' '.join(["apk", "add", packages]),
        stdout=PIPE,
        stderr=PIPE
    )

    try:
        stdout, stderr = await executor.communicate()
    except:
        return False

    stdout = stdout.decode().strip()
    stderr = stderr.decode().strip()
    if stderr and not executor.returncode:
        error(f"Apk Installer Error: {executor.returncode}: {stderr}")
    
    if executor.returncode == 0:
        return True
    return False