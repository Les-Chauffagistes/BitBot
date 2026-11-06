import traceback

from init import client, tree
from functions.loops import loop_bitcoin_price
from asyncio import gather
from settings import settings
from chauff_cmn.logging import logger as log
from ..commands.ticket import tickets as ticket

log.info("Registered on_ready")


async def stop_tasks():
    global tasks
    log.warning("Stopping tasks...")
    for task in tasks:
        try:
            task.close()

        except:
            continue


@client.event
async def on_ready():
    try:
        global tasks
        log.info('Ready!')
        tree.add_command(ticket)
        if settings.environment == "production" or settings.force_sync:
            cmds = await tree.sync()
            log.info(f'{len(cmds)} commandes slash synchronisées')


        tasks = [
            loop_bitcoin_price(),
        ]
        await gather(*tasks)

    except:
        log.warning(traceback.format_exc())
