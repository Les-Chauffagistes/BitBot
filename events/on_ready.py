import commands.badge
import commands.vente
from init import *
from functions.loops import *
from asyncio import gather
import commands.commands
import commands.pi
import commands.pi_profile
import commands.business
import commands.context
from tools.whois import start_check
from views.community_business import signin_view
from views.user_business import shop_public_view

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
        commands.pi.pi.add_command(commands.pi_profile.profile)
        tree.add_command(commands.pi.pi)
        tree.add_command(commands.vente.ventes)
        tree.add_command(commands.business.business)
        tree.add_command(commands.badge.badge)
        members = await start_check()
        log.info(members)
        
        if SYNC:
            cmds = await tree.sync()
            log.info(f'{len(cmds)} commandes slash synchronisées')
        
        embed, view = shop_public_view()
        await (await fetch(SHOP_CHANNEL_ID, SHOP_MESSAGE_ID)).edit(
            embed = embed,
            view = view
        )

        embed, view = signin_view()
        await (await fetch(SIGNIN_CHANNEL_ID, SIGNIN_MESSAGE_ID)).edit(
            embed = embed,
            view = view
        )
        
        tasks = [
            loop_miner(),
            loop_pi_deposit(),
            loop_onchain_tx(),
            loop_delete_channel()
        ]
        await gather(*tasks)

    except:
        log.warn(traceback.format_exc())