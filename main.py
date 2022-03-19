import sys
sys.dont_write_bytecode = True

from utils import app, config, logger
from asyncio import run, ensure_future
from pyrogram.methods.utilities.idle import idle

async def main():
    config.prepare()
    logger.hijack()
    logger.prepareLogBank()
    config.reloadConfig()
    config.migrate()
    
    client = app.initClient()
    from controllers import init
    ensure_future(init())
    await client.start()
    await idle()
    await client.stop()

if __name__ == "__main__":
    run(main())
