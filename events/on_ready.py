import commands.pool
from init import *
from functions.loops import *
from asyncio import gather
import commands.bitcoin
# from views.community_business import signin_view
# from views.user_business import shop_public_view

log.info("Registered on_ready")

async def stop_tasks():
    global tasks
    log.warn("Stopping tasks...")
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
        tree.add_command(commands.bitcoin.bitcoin)
        tree.add_command(commands.pool.pool)
        
        if SYNC:
            cmds = await tree.sync()
            log.info(f'{len(cmds)} commandes slash synchronisées')
        
        tasks = [
            loop_bitcoin_price(),
            loop_status(),
        ]
        await gather(*tasks)

    except:
        log.warn(traceback.format_exc())