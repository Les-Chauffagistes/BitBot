from .hashrate import Hashrate
from .abc.entity import Entity


class Worker(Entity):

    __slots__ = Entity.__slots__ + ("_name",)

    def __init__(self, workername: str, hashrate: Hashrate, last_share: int, shares: int, best_shares: float, best_ever: int):
        super().__init__(hashrate, last_share, shares, best_shares, best_ever)
        self.name = workername

    @classmethod
    def from_json(cls, data: 'Worker.RawWorker'):
        return cls(
            data['workername'],
            Hashrate.from_json(data),
            data['lastshare'],
            data['shares'],
            data['bestshare'],
            data['bestever'],
        )

    class RawWorker(Entity.RawEntity):
        workername: str

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value: str):
        self._name = value.split(".")[-1]
    
    @property
    def is_on(self) -> bool:
        return int(self.hashrate.one_minute) > 0