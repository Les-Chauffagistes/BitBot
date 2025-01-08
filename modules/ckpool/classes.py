from discord.utils import format_dt
from datetime import datetime, timedelta

class Miner:
    ___slots__ = ("miner_name", "hashrate", "best_share", "best_ever", "last_update")
    class Hashrate:
        __slots__ = ('five_mins', 'one_hour', 'one_day')
        def __init__(self, m5: float, d1: float, d7: float):
            self.five_mins = m5
            self.one_hour = d1
            self.one_day = d7
            
    def __init__(self, data: list[str]):
        self._miner_name_: str = data[0]
        self._hashrate_ = self.Hashrate(data[1], data[2], data[3])
        self._best_share_: float = data[4]
        self._best_ever_: float = data[5]
        self._last_update_: str = data[6]

    @property
    def is_on(self):
        return float(self._hashrate_.five_mins.split(' ')[0].replace(',','.')) > 0
    
    @property
    def name(self):
        return self._miner_name_.strip()
    
    @property
    def hashrate(self):
        return self._hashrate_
    
    @property
    def best_share(self):
        return self._best_share_
    
    @property
    def best_ever(self):
        return self._best_ever_
    
    @property
    def last_update(self):
        now = datetime.now()
        data = self._last_update_.split(" ")[:-1]
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