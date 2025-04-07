import abc
from typing import Any, TypedDict
from ..hashrate import Hashrate

class Entity(abc.ABC):
    __slots__ = ("_hashrate", "_last_share", "_shares", "_best_shares", "_best_ever")

    def __init__(self, hashrate: Hashrate, last_share: int, shares: int, best_shares: float, best_ever: int):
        self.hashrate = hashrate
        self.last_share = last_share
        self.shares = shares
        self.best_shares = best_shares
        self.best_ever = best_ever

    class RawEntity(TypedDict):
        hashrate1m: str
        hashrate5m: str
        hashrate1hr: str
        hashrate1d: str
        hashrate7d: str
        lastshare: int
        shares: int
        bestshare: float
        bestever: int
    
    @classmethod
    @abc.abstractmethod
    def from_json(cls, data: Any) -> 'Entity':
        pass

    @property
    def hashrate(self) -> Hashrate:
        return self._hashrate

    @hashrate.setter
    def hashrate(self, value: Hashrate):
        self._hashrate = value

    @property
    def last_share(self) -> int:
        return self._last_share

    @last_share.setter
    def last_share(self, value: int):
        self._last_share = value

    @property
    def shares(self) -> int:
        return self._shares

    @shares.setter
    def shares(self, value: int):
        self._shares = value

    @property
    def best_shares(self) -> float | int:
        return self._best_shares

    @best_shares.setter
    def best_shares(self, value: float | int):
        self._best_shares = value

    @property
    def best_ever(self) -> int:
        return self._best_ever

    @best_ever.setter
    def best_ever(self, value: int):
        self._best_ever = value
    
