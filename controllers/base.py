from os import abort
from typing import Callable, Union
from pyrogram import Client
from pyrogram.types import Message

from utils import app, logger, utils

if app.App == None:
    logger.error("Cannot call controller init before app is defined.")
    abort()

App = app.App

class Args(list):
    def get(self, index: int) -> Union[str, None]:
        if len(self) > index:
            return self[index]
        return None
    
    def getInt(self, index: int) -> int:
        return utils.toInt(self.get(index))

def onCommand(command="", filters=None, group: int = 0) -> callable:
    def decorator(func: Callable) -> Callable:
        @App.on_message(filters=filters, group=group)
        async def caller(client: Client, message: Message):
            if message.from_user.is_self and message.text:
                payloads = message.text.strip().split()
                if len(payloads) > 0 and payloads[0] == command:
                    args = Args(payloads[1:])
                    await func(args, client, message)
    
        return caller
    return decorator
