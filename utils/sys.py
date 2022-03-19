import sys
from typing import Union, List
from asyncio import create_subprocess_shell
from asyncio.subprocess import PIPE
from .logger import error

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