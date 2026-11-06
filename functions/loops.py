from settings import settings
import traceback
from aiohttp import ClientSession
from discord import Activity, ActivityType
from init import client
from asyncio import sleep, CancelledError
from chauff_cmn.logging import logger as log


async def loop_bitcoin_price():
    async with ClientSession(settings.bitcoin_api_url) as session:
        while True:
            try:
                async with session.get('/v1/bitcoin-price') as response:
                    price: int = (await response.json())['EUR']

                    await client.change_presence(
                        activity = Activity(
                            type = ActivityType.watching,
                            name = f"₿ à {price} €"
                        )
                    )

            except CancelledError:
                break

            except:
                log.warning(traceback.format_exc())

            finally:
                await sleep(60)
