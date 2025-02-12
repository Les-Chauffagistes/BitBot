from aiohttp import ClientSession
from bs4 import Tag
from discord.utils import format_dt
from datetime import datetime, timedelta
from .api import POOL_ID, make_request

class Miner:

    ___slots__ = ("miner_name", "hashrate", "best_share", "best_ever", "last_update")

    class Hashrate:

        __slots__ = ('five_mins', 'one_hour', 'one_day')

        def __init__(self, m5: str, d1: str, d7: str):
            self.five_mins = m5
            self.one_hour = d1
            self.one_day = d7
            
    def __init__(self, data: list):
        self._miner_name: str = data[0]
        self._hashrate = self.Hashrate(data[1], data[2], data[3])
        self._best_share: float = data[4]
        self._best_ever: float = data[5]
        self._last_update: str = data[6]

    @property
    def is_on(self):
        """Renvoie l'état du mineur. True s'il est allumé, False sinon"""
        return float(self._hashrate.five_mins.split(' ')[0].replace(',','.')) > 0
    
    @property
    def name(self):
        """Renvoie le nom du mineur"""
        return self._miner_name.strip()
    
    @property
    def hashrate(self):
        """Renvoie un objet hashrate"""
        return self._hashrate
    
    @property
    def best_share(self):
        """Renvoie le best share du mineur"""
        return self._best_share
    
    @property
    def best_ever(self):
        """Renvoie le best share historique du mineur"""
        return self._best_ever
    
    @property
    def last_update(self):
        """Renvoie une date formatée à laquelle CKPool a actualisé les statistiques"""
        now = datetime.now()
        data = self._last_update.split(" ")[:-1]
        elapsed_time = 0
        for i in range(0, len(data), 2):
            match data[i + 1]:
                case "days":
                    elapsed_time += 3600 * 24 * int(data[i])
                
                case "hours":
                    elapsed_time += 3600 * int(data[i])

                case "mins":
                    elapsed_time += 60 * int(data[i])
                
                case _:
                    elapsed_time += 60
                    
        return format_dt(now - timedelta(seconds = elapsed_time), 'R')
    
    @classmethod
    async def get_miner_info(cls) -> list['Miner']:
        soup = await make_request(f"/users/{POOL_ID}")
        table = soup.find('table', {'class': 'table w-full table-sm sm:table-md'})
        if isinstance(table, Tag):
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
                    "bitaxeFufu",
                    "Sulivy",
                    "GaMvugo",
                    "CariAXE"
                ]:
                    data.append(Miner(row_data))

            return data
    
        return []

    @property
    async def shares(self):
        """Total des shares du mineur"""
        soup = await make_request(f"/users/{POOL_ID}/workers/{self.name}")
        container = soup.find("div", class_="container mx-auto p-4")
        assert isinstance(container, Tag)
        # Étape 2 : Prendre la 3ème div (index 2) parmi les divs enfants
        target_div = container.find_all("div", recursive=False)[2]  # L'index est 2 car les indices commencent à 0
        if isinstance(target_div, Tag):
            # Étape 3 : Prendre la 1ère div à l'intérieur de la 3ème div
            inner_div = target_div.find_all("div", recursive=False)[0]  # Index 0 pour la première div enfant
            
            if isinstance(inner_div, Tag):
                # Étape 4 : Récupérer le texte de la 2ème div à l'intérieur
                final_div = inner_div.find_all("div", recursive=False)[1]  # Index 1 pour la 2ème div

                assert isinstance(final_div, Tag)
                text = final_div.text.strip()  # Récupé
                return text