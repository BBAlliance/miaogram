import random
from asyncio import create_subprocess_shell
from asyncio.subprocess import PIPE
from os import path

def toInt(s) -> int:
    try:
        return int(s)
    except Exception:
        return 0

def rand():
    return random.randint(0, 65535)

def randStr():
    i = rand()
    return f"{i}"

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

def convertBytes(byte):
    power = 1024
    zero = 0
    units = {
        0: '',
        1: 'Kbps',
        2: 'Mbps',
        3: 'Gbps',
        4: 'Tbps'}
    while byte > power:
        byte /= power
        zero += 1
    return f"{round(byte, 2)} {units[zero]}"