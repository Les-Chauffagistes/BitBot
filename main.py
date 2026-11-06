from init import client, routes, app, web
import bot.events.on_ready
import bot.events.on_interaction
from settings import settings
from chauff_cmn.logging import logger as log


async def main():
    log.info("Starting web server...")
    app.add_routes(routes)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', settings.port)
    await site.start()
    log.info(f'Internal web server online on localhost:{settings.port}')
    log.info("Connecting to Discord Gateway...")
    await client.login(settings.token)
    log.info("Connected")
    await client.connect()


async def clear():
    await bot.events.on_ready.stop_tasks()
    await client.close()
    client.clear()
    log.debug("Disconnected  ")


if __name__ == '__main__':
    import asyncio

    log.info("Creating an asyncio event loop...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())

    except KeyboardInterrupt:
        loop.run_until_complete(clear())
