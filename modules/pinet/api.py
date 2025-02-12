from typing import Any, Literal
from aiohttp import ClientSession
from init import log

__MAINNET_ENDPOINT__ = "https://api.mainnet.minepi.com/"
__TESTNET_ENDPOINT__ = "https://api.testnet.minepi.com/"

async def request(url: str, method: Literal['get', 'post'], network: Literal['mainnet', 'testnet']) -> dict[str, Any]:
    async with ClientSession(__TESTNET_ENDPOINT__ if network == "testnet" else __MAINNET_ENDPOINT__) as session:
        # log.debug("making request", url)
        response = await session.request(
            method,
            url,
        )
        data = await response.json()
        if data.get('status', 200) == 429:
            log.warn("rate mimit:", response.headers['x-ratelimit-limit'])
            raise Exception('Rate Limit')

        return data
