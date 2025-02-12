from datetime import datetime, timedelta, timezone
import os
import traceback
from typing import Any, cast
from discord import ButtonStyle, Embed, File, Guild, Message, Role, TextChannel
import discord
from discord.ui import Button, View
from classes.discord_wallet import PiWallet
from classes.item import CommunityItem
from functions.utils import fetch, get_user_signin_channel, mark_as_done, read_file, write_file
from init import BUYER_ROLE_ID, COLOR, GUILD_ID, MODE, SELLER_ROLE_ID, SERVER_NAME, SHOP_CHANNEL_ID, WALLET_PI_FULCRAN, client, log
from asyncio import sleep, CancelledError
from modules.ckpool import get_miners
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
            miners = await get_miners()
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
                        await tx.blacklist()
                        if wallet:
                            user = client.get_user(wallet.id)
                            if not user:
                                continue #user not found, ignoring

                            guild = cast(Guild, client.get_guild(GUILD_ID))
                            member = guild.get_member(user.id)
                            role_buyer = cast(Role, guild.get_role(BUYER_ROLE_ID))
                            role_seller = cast(Role, guild.get_role(SELLER_ROLE_ID))
                            verified = await wallet.can_transaction_verify_wallet(tx)
                            if verified:
                                log.info("--=== VERIFIED ===--")
                                await wallet.verify()

                            try:
                                match wallet.reason:
                                    case 'deposit':
                                        try:
                                            await user.send(
                                                embed = Embed(
                                                    title = "Confirmation de dépot",
                                                    description = f'Vous avez déposé {tx.amount} Pi sur votre wallet Discord.{' Bonne nouvelle, votre profil Pi a été vérifié !' if verified else ''}',
                                                    color = COLOR
                                                ).set_image(
                                                    url = 'attachment://banner.png'
                                                ),
                                                file = File("assets/pi_wallet2.png", 'banner.png')
                                            )
                                        
                                        except discord.errors.Forbidden:
                                            log.warn(f"🚫 Cannot DM {user.display_name} ({user.id})")

                                
                                    case 'seller' | 'buyer':
                                        if not member:
                                            log.warn(f"🏃‍♂️ User {user.display_name} ({user.id}) leaved guild")
                                            continue # user leaved guild, ignoring

                                        channel, message = await get_user_signin_channel(member)
                                        if wallet.reason == 'seller':
                                            role = role_seller
                                            price = 5
                                            embed = Embed(
                                                title = "Confirmation d'inscription",
                                                description = f"Félicitations, vous êtes inscrit en tant que **vendeur** sur {guild.name} ! Votre profil est désormais vérifié. Vous pouvez dès maintenant vendre des produits sur le serveur. Pour démarrer, utilisez la commande </ventes add:1327622946251866192> ici (en MP).\n En tant que vendeur, vous pouvez également acheter librement auprès d’autres vendeurs du serveur.",
                                                color = COLOR
                                            )
                                        
                                        else:
                                            role = role_buyer
                                            price = 2
                                            embed = Embed(
                                                title = "Confirmation d'inscription",
                                                description = f"Félicitations, vous êtes inscrit en tant qu’**acheteur** sur {guild.name} ! Votre profil a est désormais vérifié. Vous pouvez dès maintenant acheter des produits sur le serveur. Rendez-vous sur le salon <#{SHOP_CHANNEL_ID}> et profitez de toutes les offres des vendeurs {guild.name}.",
                                                color = COLOR
                                            )

                                        if channel and message:
                                            await mark_as_done(member)
                                            await message.delete()
                                            await channel.send(
                                                embed = embed.set_footer(
                                                    text = "Ce salon sera supprimé automatiquement au bout de 10 minutes"
                                                )
                                            )
                                        
                                        else:
                                            try:
                                                await user.send(embed = embed)
                                            
                                            except discord.errors.Forbidden:
                                                pass

                                        if not role in member.roles:
                                            await wallet.remove_pi(price)

                                        await member.add_roles(role)
                            
                            except:
                                log.warn("Unhandled error in dispatcher:", traceback.format_exc())
                                pass
        
        except CancelledError:
            log.info("Stopping loop...")
            break
        
        except:
            log.warn("Unhandled error in loop:", traceback.format_exc())
            
        finally:
            await sleep(15)
            continue

async def loop_onchain_tx():
    log.info("Ready")
    while True:
        try:
            for sale_file in os.listdir("data/business/sales"):
                try:
                    item = await CommunityItem.from_id(sale_file.split(".")[0])
                    assert item
                    if not await item.message:
                        continue # skip item

                    seller_wallet = await PiWallet.from_user(item.seller_id)
                    assert seller_wallet

                    onchain_wallet = seller_wallet.on_chain
                    if not onchain_wallet:
                        continue # Could be None if address is removed
                
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
                                        guild = cast(Guild, client.get_guild(GUILD_ID))
                                        member = guild.get_member(wallet.id)
                                        assert member
                                        if item.sell_type == "unique":
                                            message = await item.message
                                            if message:
                                                button: Button = message.components[0].children[0] #type: ignore
                                                new_button = Button()
                                                new_button.label = button.label
                                                new_button.emoji = button.emoji
                                                new_button.custom_id = button.custom_id
                                                new_button.disabled = True
                                                new_button.style = ButtonStyle.gray
                                                await message.edit(
                                                    view = View().add_item(new_button)
                                                )

                                        await payment.notify()
                                        assert item.seller
                                        assert client.user
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
            let: dict[str, dict[str, Any]] = {}
            data = cast(dict[str, dict[str, int]], await read_file("business/signin_channels.json"))
            for user_id, channel_data in data.items():
                end_date: int = channel_data.get("done", 0)
                if end_date: # Expired channel, deleting
                    try:
                        channel = cast(TextChannel, client.get_channel(channel_data.get("channel_id", 0)))
                        if not channel:
                            continue
                        
                        if datetime.fromtimestamp(end_date) + timedelta(minutes = 10) < datetime.now() :
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