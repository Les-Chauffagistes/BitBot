import asyncio
import signal
from init import client, routes, app, web
import bot.events.on_ready
import bot.events.on_interaction
import server.handlers
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

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, stop.set)

    connection = asyncio.create_task(client.connect())
    stopper = asyncio.create_task(stop.wait())
    try:
        await asyncio.wait({connection, stopper}, return_when=asyncio.FIRST_COMPLETED)
        if stop.is_set():
            log.info("Shutdown signal received, stopping...")
    finally:
        connection.cancel()
        stopper.cancel()
        await clear()
        await runner.cleanup()


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
    loop.run_until_complete(main())
