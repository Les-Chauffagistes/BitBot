import commands.vente
from init import *
from functions.loops import *
from asyncio import gather
import commands.commands
import commands.pi
import commands.pi_profile
import commands.business

log.info("Registered on_ready")

async def stop_tasks():
    global tasks
    log.warn("Stopping tasks...")
    for task in tasks:
        try:
            task.cancel()
        
        except:
            continue

@client.event
async def on_ready():
    try:
        global tasks
        log.info('Ready!')
        commands.pi.pi.add_command(commands.pi_profile.profile)
        tree.add_command(commands.pi.pi)
        tree.add_command(commands.vente.ventes)
        tree.add_command(commands.business.business)
        if SYNC:
            cmds = await tree.sync()
            log.info(f'{len(cmds)} commandes slash synchronisées')
        
        tasks = [
            loop_miner(),
            loop_pi_deposit(),
            loop_onchain_tx(),
            loop_delete_channel()
        ]
        await gather(*tasks)

    except:
        log.warn(traceback.format_exc())