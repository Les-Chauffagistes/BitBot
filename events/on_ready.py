from init import *
from functions.loops import *
from asyncio import gather
import commands.commands

async def stop_task():
    global tasks
    for task in tasks:
        try:
            task.cancel()
        
        except:
            continue

@client.event
async def on_ready():
    global tasks
    log.info('En ligne')
    if SYNC:
        cmds = await tree.sync()
        log.info(f'{len(cmds)} commandes slash synchronisées')
    
    tasks = []
    await gather(*tasks)