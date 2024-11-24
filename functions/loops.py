import traceback
from discord import Embed, File
from classes.discord_wallet import PiWallet
from functions.utils import fetch
from init import COLOR, MODE, SERVER_NAME, WALLET_PI_FULCRAN, client, log
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