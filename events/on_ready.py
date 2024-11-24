from discord import ButtonStyle
from classes.emoji import Emoji
import commands.vente
from init import *
from functions.loops import *
from asyncio import gather
import commands.commands
import commands.pi
import commands.pi_profile
from discord.ui import View, Button

async def stop_task():
    global tasks
    for task in tasks:
        try:
            task.cancel()
        
        except:
            continue

@client.event
async def on_ready():
    try:
        global tasks
        log.info('En ligne')
        commands.pi.pi.add_command(commands.pi_profile.profile)
        tree.add_command(commands.pi.pi)
        tree.add_command(commands.vente.ventes)
        inscriptions = await fetch(1310229664244961361, 1310229676383277121)
        await inscriptions.edit(
            embed = Embed(
                title = "Commerce Pi Network",
                description = """
# Vendre et acheter avec ses Pi
Inscrivez vous en tant qu'acheteur ou vendeur pour enrichir votre expérience autour de Pi Network.
## En tant qu'acheteur
Vous pouvez participer aux enchères et acheter des produits mis en vente sur Discord. Vous pouvez payer via votre wallet Mainnet ou Discord.
## En tant que vendeur
Vous recevez tous les privilèges d'acheteur, en plus du droit de créer des enchères, et de mettre en vente des articles sur Discord. Vous choisissez les modalité de paiement et d'envoi des produits physiques.

> Les inscriptions sont soumises aux conditions de services. Consultez les [conditions de vente](https://swakraft.hopto.org/pilabs/terms) et la [charte du vendeur](https://swakraft.hopto.org/pilabs/guidelines). Nécessite un profil Pi vérifié sur le serveur.
""".strip(),
                color = COLOR
            ),
            view = View(timeout = None).add_item(
                Button(
                    label = "Devenir Vendeur",
                    style = ButtonStyle.blurple,
                    emoji = Emoji.store.value,
                    custom_id = "BECOME_SELLER",
                )
            ).add_item(
                Button(
                    label = "Devenir Acheteur",
                    emoji = Emoji.cart.value,
                    custom_id = "BECOME_BUYER",
                )
            )
        )
        if SYNC:
            cmds = await tree.sync()
            log.info(f'{len(cmds)} commandes slash synchronisées')
        
        tasks = [
            loop_miner(),
            loop_pi_deposit()
        ]
        await gather(*tasks)

    except:
        log.warn(traceback.format_exc())
