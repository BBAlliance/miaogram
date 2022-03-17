from controllers.base import reloadPlugins

async def init():
    await reloadPlugins()
