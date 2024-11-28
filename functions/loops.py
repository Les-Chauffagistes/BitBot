import os
import traceback
from discord import Embed, File, Member, User
from classes.discord_wallet import PiWallet
from classes.item import Item
from functions.utils import fetch, read_file
from init import COLOR, GUILD_ID, MODE, SERVER_NAME, WALLET_PI_FULCRAN, client, log
from asyncio import sleep, CancelledError
from modules.ckpool.api import get_miner_info
from modules.pinet.classes import Wallet

async def loop_miner():
    log.info("Ready")
    if MODE == "DEV":
        dashboard = await fetch(1309917142736703622, 1309925491146358794)

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
            for tx in history:
                tx = await tx.payment
                if tx.source != wallet_fulcran.address:
                    if not await tx.is_blacklist():
                        wallet = await PiWallet.add_to_wallet(tx.amount)
                        if wallet:
                            #log.info('Added', tx.amount, 'to wallet')
                            await tx.blacklist()
                            if wallet.validation_amount == tx.amount and not wallet.is_verified and (wallet.address.upper() if wallet.address else None) == tx.source.address.upper():
                                log.info("! VERIFIED !")
                                await wallet.verify()
                                #wallet.validation_amount = None
                                try:
                                    await client.get_user(wallet.id).send(
                                        embed = Embed(
                                            title = "Votre profil a été validé !",
                                            description = f"Bonne nouvelle, votre profil Pi Network a été vérifié. Votre profil vérifié vous permet de participer au commerce Pi Network sur Discord. Désormais, vous pouvez vous inscrire en tant qu'acheteur ou vendeur sur le serveur {SERVER_NAME}.\nVous aves également reçu {tx.amount} Pi sur votre wallet Discord.\n\nRappel amical: BitBot ne vous demandera jamais votre passphrase. Restez vigilant, et méfiez vous du fishing.",
                                            color = COLOR
                                        ).set_image(
                                            url = "attachment://pi_wallet2.png",
                                        ),
                                        file = File("assets/pi_wallet2.png")
                                    )
                                
                                except:
                                    log.warn(traceback.format_exc())
                                    pass
                            
                            else:
                                try:
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
                                
                                except:
                                    log.warn(traceback.format_exc())
                                    #log.debug('Cant mp')
                                    pass
                                #log.info("Not verified")
                                pass
                    
                    else:
                        #log.debug('Blacklisted')
                        pass
                
                else:
                    #log.debug('Not a deposit')
                    pass
        
        except CancelledError:
            break
        
        except:
            log.warn(traceback.format_exc())
            
        finally:
            await sleep(5)
            continue

async def loop_onchain_tx():
    log.info("Ready")
    while True:
        try:
            for sale_file in os.listdir("data/business/sales"):
                try:
                    item = Item(**await read_file(f"business/sales/{sale_file}"))
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
                    for transaction in transactions:
                        payment = await transaction.payment
                        try:
                            if await payment.is_notified():
                                continue # skip searching and check next payment

                            log.info(f"checking ({payment.amount} π)")
                            if payment.amount == item.price and payment.destination.address == onchain_wallet.address:
                                log.info(f'payment found ({item.name})')
                                for wallet_file in os.listdir("data/wallets/pi"):
                                    try:
                                        wallet = await PiWallet.from_file(f"wallets/pi/{wallet_file}")
                                        if wallet.address == payment.source.address:
                                            log.info(f"buyer found {wallet.id}")
                                            guild = client.get_guild(GUILD_ID)
                                            member = guild.get_member(wallet.id)
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
            await sleep(15)