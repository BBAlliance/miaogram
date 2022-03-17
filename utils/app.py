import sys
from pyrogram import Client
from .config import DataDir

import signal

App: Client = None

def initClient(sessionName: str="miaogram"):
    global App
    App = Client(sessionName, workdir=DataDir)
    
    return App

NeedExit = False
def _need_exit():
    global NeedExit
    NeedExit = True
    sys.exit(1)

def Killed():
    return NeedExit

signal.signal(signal.SIGINT, _need_exit)
signal.signal(signal.SIGTERM, _need_exit)