import traceback
from aiohttp import ClientSession
from discord import Activity, ActivityType
from init import client, log, storage
from asyncio import sleep, CancelledError

log.info("Creating tasks")

async def loop_bitcoin_price():
    log.info("Ready")
    while True:
        try:
            async with ClientSession('https://swakraft.fr/api/') as session:
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