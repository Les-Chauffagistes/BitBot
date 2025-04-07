from aiohttp import ClientSession
from bs4 import BeautifulSoup, Tag

# Étape 1 : Récupérer la page
url = 'https://solostats.ckpool.org/users/bc1qh8ge36h2njrp2aqv5ddpyph4g22elzgkds52ae'

__ENDPOINT__ = 'https://solostats.ckpool.org'
POOL_ID = 'bc1qh8ge36h2njrp2aqv5ddpyph4g22elzgkds52ae'

async def make_request(url: str):
    async with ClientSession(__ENDPOINT__) as session:
        async with session.get(url) as response:
            response.raise_for_status()
            soup = BeautifulSoup(await response.text(), 'html.parser')
            return soup