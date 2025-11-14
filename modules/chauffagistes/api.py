from aiohttp import ClientSession
from os import getenv


async def get_infos():
    async with ClientSession("https://chauffagistes-pool.fr:3000/") as session:
        async with session.get(
            "api/data", 
            headers = {
                "Authorization": f"Bearer {getenv('CHAUFFAGISTES_API_KEY')}"
            }
        ) as response:
            return await response.json()