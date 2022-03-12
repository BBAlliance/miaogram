from asyncio import create_subprocess_shell, sleep
from asyncio.subprocess import PIPE
from os import path
from threading import Thread

import random

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
