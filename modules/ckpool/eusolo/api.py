import asyncio
import json
from aiohttp import ClientSession

from .model.pool import Pool

# Étape 1 : Récupérer la page
url = 'https://eusolo.ckpool.org/users/bc1qh8ge36h2njrp2aqv5ddpyph4g22elzgkds52ae'

__ENDPOINT__ = 'https://eusolo.ckpool.org'
POOL_ID = 'bc1qh8ge36h2njrp2aqv5ddpyph4g22elzgkds52ae'

async def _make_request(url: str):
    async with ClientSession(__ENDPOINT__) as session:
        async with session.get(url) as response:
            response.raise_for_status()
            raw_data = await response.text()
            return json.loads(raw_data)

async def get_user(id: str):
    data = await _make_request(f"/users/{id}")
    pool = Pool.from_json(data)
    return pool