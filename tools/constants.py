from aiohttp import ClientSession

PI_COIN_VALUE = 0.001

async def update_pi_coin_value():
    async with ClientSession("https://blockchain.pinet/mainnet") as session:
        payload = {
            "network": "mainnet",
            "type": "constant",
            "key": "PI_COIN_VALUE",
            "value": PI_COIN_VALUE
        }
        async with session.post("/price", json = payload) as response:
            response.raise_for_status()
            return await response.json()