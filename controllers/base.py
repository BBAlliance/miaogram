from os import abort
from typing import Callable, Union
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.handlers import MessageHandler

from utils import app, logger, utils

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

groupNum = 0
def onCommand(command="", filters=None) -> callable:
    def decorator(func: Callable) -> Callable:
        global groupNum
        async def caller(client: Client, message: Message):
            if message and message.from_user and message.from_user.is_self and message.text:
                payloads = message.text.strip().split()
                if len(payloads) > 0 and payloads[0] == command:
                    logger.info(f"Calling plugin: {command} with={payloads[1:]}")
                    args = Args(payloads[1:])
                    try:
                        await func(args, client, message)
                    except Exception as e:
                        logger.error(f"Unexpected Error: {e}")
        
        App.add_handler(MessageHandler(caller, filters), groupNum)
        groupNum += 1
        return caller
    return decorator

def onMessage(filters=None) -> callable:
    def decorator(func: Callable) -> Callable:
        global groupNum
        async def caller(client: Client, message: Message):
            try:
                await func(client, message)
            except Exception as e:
                logger.error(f"Unexpected Error: {e}")
        
        App.add_handler(MessageHandler(caller, filters), groupNum)
        groupNum += 1
        return caller
    return decorator