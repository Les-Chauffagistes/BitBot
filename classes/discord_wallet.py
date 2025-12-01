import os
from typing import TypedDict, cast
from functions.utils import read_file, write_file


class BaseDiscordWallet:
    __slots__ = ("id", "balance")

    def __init__(self, user_id: int, balance: float) -> None:
        self.id = user_id
        self.balance = balance

    async def save(self):
        raise NotImplementedError

    def start_validation(self):
        raise NotImplementedError

    class BaseError(Exception):
        pass

    class FundsError(BaseError):
        pass


class BitcoinWallet(BaseDiscordWallet):

    __slots__ = ("_user_id", "_balance")

    def __init__(self, id: int, balance: int) -> None:
        self._user_id = id
        self._balance = balance

    @property
    def balance(self):
        return self._balance

    @property
    def id(self):
        return self._user_id

    class types(TypedDict):
        id: int
        balance: int

    @classmethod
    async def from_file(cls, file: str):
        data = cast(BitcoinWallet.types, await read_file(file))
        return cls(**data)

    @classmethod
    async def _new(cls, for_user: int):
        wallet = cls(for_user, 0)
        await wallet.save()
        return wallet

    @classmethod
    async def from_user_id(cls, user_id: int):
        """Returns the user's wallet. Create a new one if it doesn't exist"""
        for wallet_file in os.listdir("data/wallets/bitcoin"):
            if wallet_file.startswith(str(user_id)):
                return await cls.from_file(f"wallets/bitcoin/{wallet_file}")

        else:
            return await cls._new(user_id)

    @property
    def json(self):
        return {"id": self._user_id, "balance": self._balance}

    async def save(self):
        await write_file(f"wallets/bitcoin/{self._user_id}.json", self.json)

    async def add_sat(self, amount: int):
        assert amount > 0
        self._balance += amount
        await self.save()
        return self

    async def remove_sat(self, amount: int):
        assert amount > 0
        if self._balance < amount:
            raise self.FundsError

        self._balance -= amount
        await self.save()
        return self

    async def send(self, amount: int, wallet: "BitcoinWallet"):
        await self.remove_sat(amount)
        if wallet.id == self.id:
            wallet = self
        await wallet.add_sat(amount)
