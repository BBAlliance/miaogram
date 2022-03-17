from controllers.base import reloadPlugins, startScheduler

async def init():
    await reloadPlugins()
    startScheduler()
