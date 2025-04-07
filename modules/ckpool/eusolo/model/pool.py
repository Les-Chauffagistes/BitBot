from .worker import Worker
from .abc.entity import Entity
from .hashrate import Hashrate


class Pool(Entity):

    __slots__ = Entity.__slots__ + ("_workers", "_authorized")

    def __init__(self, hashrate: Hashrate, last_share: int, shares: int, best_shares: float, best_ever: int, workers: list[Worker], authorized: int):
        super().__init__(hashrate, last_share, shares, best_shares, best_ever)
        self._workers = workers
        self.authorized = authorized

    class RawPool(Entity.RawEntity):
        workers: int
        authorised: int
        worker: list[Worker.RawWorker]
    
    @classmethod
    def from_json(cls, data:RawPool):
        workers: list[Worker] = []
        for raw_worker in data["worker"]:
            workers.append(Worker.from_json(raw_worker))

        return cls(
            hashrate=Hashrate.from_json(data),
            last_share=data["lastshare"],
            shares=data["shares"],
            best_shares=data["bestshare"],
            best_ever=data["bestever"],
            workers=workers,
            authorized=data["authorised"],
        )
    
    @property
    def workers(self):
        return self._workers.copy()

    @property
    def authorized(self):
        return self._authorized

    @authorized.setter
    def authorized(self, value):
        self._authorized = value