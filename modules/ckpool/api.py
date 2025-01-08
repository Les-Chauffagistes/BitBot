from aiohttp import ClientSession
from bs4 import BeautifulSoup
from .classes import Miner

# Étape 1 : Récupérer la page
url = 'https://solostats.ckpool.org/users/bc1qh8ge36h2njrp2aqv5ddpyph4g22elzgkds52ae'

__ENDPOINT__ = 'https://solostats.ckpool.org'
POOL_ID = 'bc1qh8ge36h2njrp2aqv5ddpyph4g22elzgkds52ae'

async def get_miner_info() -> list[Miner] | None:
    async with ClientSession(__ENDPOINT__) as session:
        async with session.get(f'/users/{POOL_ID}') as response:
            response.raise_for_status()

            soup = BeautifulSoup(await response.text(), 'html.parser')
            table = soup.find('table', {'class': 'table w-full table-sm sm:table-md'})
            if table:
                rows = table.find_all('tr')
                data = []
                for row in rows[1:]:
                    cells = row.find_all(['td', 'th'])
                    row_data = [cell.get_text(strip = True) for cell in cells]
                    if row_data[0] in [
                        "ITS9",
                        "Gamma-Fufu",
                        "Supra-WaL",
                        "fufus9",
                        "Tittou-S9",
                        "bitaxeFufu"
                    ]:
                        data.append(Miner(row_data))

                return data

            else:
                return None