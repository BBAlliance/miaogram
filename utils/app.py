from pyrogram import Client

App: Client = None

def initClient(sessionName: str="miaogram"):
    global App
    App = Client(sessionName)
    
    return App