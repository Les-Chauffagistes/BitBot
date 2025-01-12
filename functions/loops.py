from datetime import datetime, timedelta, timezone
import os
from socket import timeout
import traceback
from discord import ButtonStyle, Embed, File
from discord.ui import Button, View
from classes.discord_wallet import PiWallet
from classes.item import CommunityItem
from functions.utils import fetch, get_user_signin_channel, mark_as_done, read_file, write_file
from init import BUYER_ROLE_ID, COLOR, GUILD_ID, MODE, SELLER_ROLE_ID, SERVER_NAME, WALLET_PI_FULCRAN, client, log
from asyncio import sleep, CancelledError
from modules.ckpool.api import get_miner_info
from modules.pinet.classes import Wallet
import discord.utils as utils

log.info("Creating tasks")

async def loop_miner():
    log.info("Ready")
    if MODE == "DEV":
        dashboard = await fetch(1309917142736703622, 1309925491146358794)

    else:
        dashboard = await fetch(1287747648564105307, 1287747811798024302)

    while True:
        try: # Loop instructions
            miners = await get_miner_info()
            txt = ""
            for miner in miners:
                txt += f"{'🟢' if miner.is_on else '🔴'} **{miner.name} :** `{miner.hashrate.one_day}` {miner.last_update}\n"

            await dashboard.edit(
                embed = Embed(
                    title = "Pool - Infos pour 24 heures",
                    description = txt,
                    color = COLOR
                )
            )

        except CancelledError: # Task cancelled (stopping bot)
            break

        except: # Unknown error
            log.warn(traceback.format_exc())
        
        finally:
            await sleep(300)

async def loop_pi_deposit():
    log.info("Ready")
    wallet_fulcran = Wallet(WALLET_PI_FULCRAN)
    log.info("Listening for txs...")
    while True:
        try:
            if MODE == "DEV":
                history = await wallet_fulcran.get_testnet_history()
            
            else:
                history = await wallet_fulcran.get_mainnet_history()

            #log.debug(f'Scanning {len(history)} transactions...')
            await sleep(2)
            for tx in history:
                if not await tx.is_blacklist():
                    tx = await tx.payment
                    await sleep(5)
                    if tx.source != wallet_fulcran.address:
                        wallet = await PiWallet.add_to_wallet(tx.amount)
                        if wallet:
                            #log.info('Added', tx.amount, 'to wallet')
                            await tx.blacklist()
                            user = client.get_user(wallet.id)
                            guild = client.get_guild(GUILD_ID)
                            member = guild.get_member(user.id)
                            role_buyer = guild.get_role(BUYER_ROLE_ID)
                            role_seller = guild.get_role(SELLER_ROLE_ID)
                            if wallet.validation_amount == tx.amount and not wallet.is_verified and (wallet.address.upper() if wallet.address else None) == tx.source.address.upper():
                                log.info("! VERIFIED !")
                                await wallet.verify()
                                #wallet.validation_amount = None
                                try:

                                    match wallet.reason:
                                        case 'deposit':
                                            await user.send(
                                                embed = Embed(
                                                    title = "Votre profil a été validé !",
                                                    description = f"Bonne nouvelle, votre profil Pi Network a été vérifié. Votre profil vérifié vous permet de participer au commerce Pi Network sur Discord. Désormais, vous pouvez vous inscrire en tant qu'acheteur ou vendeur sur le serveur {SERVER_NAME}.\nVous aves également reçu {tx.amount} Pi sur votre wallet Discord.\n\nRappel amical: BitBot ne vous demandera jamais votre passphrase. Restez vigilant, et méfiez vous du fishing.",
                                                    color = COLOR
                                                ).set_image(
                                                    url = "attachment://pi_wallet2.png",
                                                ),
                                                file = File("assets/pi_wallet2.png")
                                            )
                                    
                                        case 'seller':
                                            channel, message = await get_user_signin_channel(member)
                                            await mark_as_done(member)
                                            await message.delete()
                                            await channel.send(
                                                embed = Embed(
                                                    title = "Inscription confirmée !",
                                                    description = f"Votre inscription en tant que vendeur a bien été prise en compte. Voici tout ce que vous pouvez faire de génial sur {SERVER_NAME} désormais:\n- Mettre en vente des produits\n- Créer des enchères\n- Acheter des produits vendus par la communauté\n- Acheter dans la boutique **Fulcran**\n- Participer aux enchères d'autres membres du serveur\n\nRappel amical: BitBot ne vous demandera jamais votre passphrase. Restez vigilant, et méfiez vous du fishing.",
                                                    color = COLOR
                                                ).set_footer(
                                                    text = "Ce salon sera supprimé automatiquement au bout de 10 minutes"
                                                )
                                            )
                                            await wallet.remove_pi(5)
                                            await member.add_roles(role_seller)
                                        
                                        case 'buyer':
                                            channel, message = await get_user_signin_channel(member)
                                            await mark_as_done(member)
                                            await message.delete()
                                            await channel.send(
                                                    embed = Embed(
                                                        title = "Inscription confirmée !",
                                                        description = f"Votre inscription en tant qu'acheteur a bien été prise en compte. Vous pouvez désormais acheter sur le serveur et participer aux enchères sur le serveur !",
                                                        color = COLOR
                                                    ).set_footer(
                                                        text = "Ce salon sera supprimé automatiquement au bout de 10 minutes"
                                                    )
                                                )
                                            await wallet.remove_pi(2)
                                            await member.add_roles(role_buyer)
                                
                                except:
                                    log.warn(traceback.format_exc())
                                    pass
                            
                            else:
                                try:
                                    match wallet.reason:
                                        case "deposit":
                                            await client.get_user(wallet.id).send(
                                                embed = Embed(
                                                    title = "Confirmation de dépot",
                                                    description = f"Vous avez déposé {tx.amount} Pi sur votre wallet Pi Discord",
                                                    color = COLOR
                                                ).set_image(
                                                    url = "attachment://pi_wallet2.png",
                                                ),
                                                file = File("assets/pi_wallet2.png")
                                            )
                                        
                                        case "seller":
                                            if wallet.validation_amount == tx.amount and wallet.address.upper() == tx.source.address.upper():
                                                await mark_as_done(user)
                                                await client.get_user(wallet.id).send(
                                                    embed = Embed(
                                                        title = "Inscription confirmée !",
                                                        description = "Votre wallet Pi a été validé et votre inscription a bien été payée. Vous pouvez commencer à vendre sur le serveur !",
                                                        color = COLOR
                                                    )
                                                )
                                                channel, message = await get_user_signin_channel(member)
                                                await message.delete()
                                                await channel.send(
                                                    embed = Embed(
                                                        title = "Inscription confirmée !",
                                                        description = f"Votre inscription en tant que vendeur a bien été prise en compte. Voici tout ce que vous pouvez faire de génial sur {SERVER_NAME} désormais:\n- Mettre en vente des produits\n- Créer des enchères\n- Acheter des produits vendus par la communauté\n- Acheter dans la boutique **Fulcran**\n- Participer aux enchères d'autres membres du serveur\n\nRappel amical: BitBot ne vous demandera jamais votre passphrase. Restez vigilant, et méfiez vous du fishing.",
                                                        color = COLOR
                                                    ).set_footer(
                                                        text = "Ce salon sera supprimé automatiquement au bout de 10 minutes"
                                                    )
                                                )
                                                await wallet.remove_pi(5)
                                                await member.add_roles(role_seller)
                                            
                                        case "buyer":
                                            if wallet.validation_amount == tx.amount and wallet.address.upper() == tx.source.address.upper():
                                                channel, message = await get_user_signin_channel(member)
                                                await mark_as_done(member)
                                                await message.delete()
                                                await channel.send(
                                                    embed = Embed(
                                                        title = "Inscription confirmée !",
                                                        description = f"Votre inscription en tant qu'acheteur a bien été prise en compte. Vous pouvez désormais acheter sur le serveur et participer aux enchères sur le serveur !",
                                                        color = COLOR
                                                    ).set_footer(
                                                        text = "Ce salon sera supprimé automatiquement au bout de 10 minutes"
                                                    )
                                                )
                                                await wallet.remove_pi(2)
                                                await member.add_roles(role_buyer)
                                        
                                except:
                                    log.warn(traceback.format_exc())
                                    #log.debug('Cant mp')
                                    pass
                                #log.info("Not verified")
                                pass
                    
                    else:
                        #log.debug('Not a deposit')
                        pass

                    await tx.blacklist()
        
        except CancelledError:
            break
        
        except:
            log.warn(traceback.format_exc())
            
        finally:
            await sleep(15)
            continue

async def loop_onchain_tx():
    log.info("Ready")
    while True:
        try:
            for sale_file in os.listdir("data/business/sales"):
                try:
                    item = CommunityItem(**await read_file(f"business/sales/{sale_file}"))
                    if not await item.message:
                        continue # skip item

                    seller_wallet = await PiWallet.from_user(item.seller_id)
                    onchain_wallet = seller_wallet.on_chain
                
                except:
                    log.warn("Unable to read sale file or load seller wallet")
                    log.warn(traceback.format_exc())
                    continue
            
                if MODE == "DEV":
                    #log.info(f"checking {item.name}")
                    transactions = await onchain_wallet.get_testnet_history()
                
                else:
                    transactions = await onchain_wallet.get_mainnet_history()
                    
                for transaction in transactions:
                    payment = await transaction.payment
                    await sleep(1)
                    try:
                        if await payment.is_notified():
                            continue # skip searching and check next payment

                        log.info(f"checking ({payment.amount} π)")
                        await sleep(1)
                        if payment.amount == item.price and payment.destination.address == onchain_wallet.address:
                            log.info(f'payment found ({item.name})')
                            for wallet_file in os.listdir("data/wallets/pi"):
                                try:
                                    wallet = await PiWallet.from_file(f"wallets/pi/{wallet_file}")
                                    if wallet.address == payment.source.address:
                                        log.info(f"buyer found {wallet.id}")
                                        guild = client.get_guild(GUILD_ID)
                                        member = guild.get_member(wallet.id)
                                        if item.sell_type == "unique":
                                            message = await item.message
                                            if message:
                                                button: Button = message.components[0].children[0]
                                                new_button = Button()
                                                new_button = Button()
                                                new_button.label = button.label
                                                new_button.emoji = button.emoji
                                                new_button.custom_id = button.custom_id
                                                new_button.disabled = True
                                                new_button.style = ButtonStyle.gray
                                                await message.edit(
                                                    view = View(timeout).add_item(new_button)
                                                )

                                        await payment.notify()
                                        await item.seller.send(
                                            embed = Embed(
                                                title = "Un paiement a été trouvé sur la blockchain",
                                                description = f"{client.user.display_name} a trouvé un paiement sur la blockchain qui semble correspondre à l'achat d'un article que vous vendez sur le serveur {guild.name}.\n### Détails\nArticle: {item.name}\nPrix: {item.price} π\nAcheteur: {member.display_name}\nVérifiez que ces informations sont correctes en vous rapprochant via MP",
                                                color = COLOR
                                            )
                                        )
                                        await member.send(
                                            embed = Embed(
                                                title = "Votre paiement à été trouvé sur la blockchain",
                                                description = f"La transaction de {payment.amount} π depuis votre wallet a été trouvée sur la blockchain pour l'achat de {item.name}. Veuillez vous rapprocher de {client.user.display_name} pour confirmer la l'envoi.",
                                                color = COLOR
                                            )
                                        )
                                        break

                                    else:
                                        await payment.notify()
                                        log.info(f"mismach source\n", {payment.source.address}, {wallet.address})
                                
                                except:
                                    log.warn(traceback.format_exc())
                                    continue
                        
                        else:
                            await payment.notify()
                            log.info(f"missmach", payment.amount == item.price, payment.destination == onchain_wallet.address)
                    
                    except:
                        log.warn(traceback.format_exc())
                        continue

        except CancelledError:
            break

        except:
            log.warn(traceback.format_exc())

        finally:
            await sleep(30)

async def loop_delete_channel():
    log.info("Ready")
    while True:
        try:
            let = {}
            for user_id, channel_data in (await read_file("business/signin_channels.json")).items():
                end_date: int = channel_data.get("done", 0)
                if end_date: # Expired channel, deleting
                    try:
                        channel = client.get_channel(channel_data.get("channel_id"))
                        log.debug(datetime.fromtimestamp(end_date) + timedelta(minutes = 10), datetime.now(tz=timezone.utc))
                        if end_date + timedelta(minutes = 10) < datetime.now(tz=timezone.utc) :
                            await channel.delete(reason = "Inscription terminée")
                        
                        else: # Not expired, conserving
                            let[user_id] = channel_data
                    
                    except:
                        log.warn("y'a eu un problemo:", traceback.format_exc())
                        continue

                else: # Still active, conserving
                    let[user_id] = channel_data
            
            await write_file("business/signin_channels.json", let)
        
        except CancelledError:
            break

        except:
            log.warn(traceback.format_exc())

        finally:
            await sleep(15)