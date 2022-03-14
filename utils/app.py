from pyrogram import Client
from os.path import join, dirname
from .config import DataDir

App: Client = None

def initClient(sessionName: str="miaogram"):
    global App
    App = Client(sessionName, workdir=DataDir)
    
    return App