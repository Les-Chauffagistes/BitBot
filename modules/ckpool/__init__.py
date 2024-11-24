from typing import Literal
from aiohttp import ClientSession

__MAINNET_ENDPOINT__ = "https://api.mainnet.minepi.com/"
__TESTNET_ENDPOINT__ = "https://api.testnet.minepi.com/"

async def request(url: str, method: Literal['get', 'post'], network: Literal['mainnet', 'testnet']) -> dict | list:
    async with ClientSession(__TESTNET_ENDPOINT__ if network == "testnet" else __MAINNET_ENDPOINT__) as session:
        return await (await session.request(
            method,
            url,
        )).json()