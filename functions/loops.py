import os, traceback
from aiohttp import ClientSession
from discord import Embed, Activity, ActivityType
from functions.utils import fetch
from init import COLOR, MODE, client, log, storage
from asyncio import sleep, CancelledError
from modules.ckpool import eusolo

log.info("Creating tasks")

async def loop_miner():
    log.info("Ready")
    if MODE == "DEV":
        dashboard = await fetch(1309917142736703622, 1309925491146358794)

    else:
        dashboard = await fetch(1287747648564105307, 1287747811798024302)
    
    log.debug("Waiting for bitcoin block reward")
    while not storage.bitcoin_block_reward:
        await sleep(0.1)
    
    log.debug("Got reward")

    while True:
        try: # Loop instructions
            pool = await eusolo.get_user(eusolo.POOL_ID)
            txt = "```\n"
            txt += f"{'  '} {'Nom':<10} {'Shares':>9} {'Reward':>9} {'Valeur (€)':>11}\n"
            txt += "-" * 49 + "\n"

            for worker in pool.workers:
                worker_percent = worker.shares / pool.shares
                worker_reward = worker_percent * storage.bitcoin_block_reward
                status = "🟢" if worker.is_on else "🔴"
                
                txt += f"{status} {worker.name:<10} {round(worker_percent * 100, 1):>7} % {round(worker_reward, 4):>7} ₿ {round(worker_reward * storage.bitcoin_price, 2):>9} €\n"

            txt += "```"
            await dashboard.edit(
                embed = Embed(
                    title = "Pool - Infos instantanées",
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

async def loop_bitcoin_price():
    log.info("Ready")
    while True:
        try:
            async with ClientSession('https://swakraft.hopto.org/api/') as session:
                async with session.get('bitcoin-price') as response:
                    log.debug(await response.text())
                    price: int = (await response.json())['EUR']

                    storage.bitcoin_price = price
                
                async with session.get('bitcoin-block-reward') as response:
                    log.debug(await response.text())
                    reward: float = float(await response.text())

                    storage.bitcoin_block_reward = reward
        
        except CancelledError:
            break

        except:
            log.warn(traceback.format_exc())

        finally:
            await sleep(60)
            continue
    
async def loop_status():
    log.info("Ready, waiting...")
    while not storage.bitcoin_price:
        await sleep(0.1)

    log.info("Got price")
    while True:
        try:
            price: str = f"{storage.bitcoin_price:,}".replace(",", " ")
            await client.change_presence(
                activity = Activity(
                    type = ActivityType.watching,
                    name = f"₿ à {price} €"
                )
            )
        
        except CancelledError:
            break

        except:
            log.warn(traceback.format_exc())

        finally:
            await sleep(60)