import os
from random import randint
from typing import Optional
from functions.utils import read_file, write_file
from views.pi_wallet import deposit_view, validation_view

class BaseDiscordWallet:
    __slots__ = ('id', 'verified', 'balance', 'validation_amount')

    def __init__(self, user_id: int, verified: bool, balance: float, validation_amount: Optional[float]) -> None:
        self.user_id = user_id
        self.verified = verified
        self.balance = balance
        self.validation_amount = validation_amount

    async def save(self):
        raise NotImplementedError

    def start_validation(self):
        raise NotImplementedError

class PiWallet(BaseDiscordWallet):
    __slots__ = ('id', 'verified', 'balance', 'validation_amount', 'payments_ids')

    def __init__(self, user_id: int, verified: bool, balance: float, validation_amount: Optional[float], payments_ids: list[int]):
        super().__init__(user_id, verified, balance, validation_amount)
        self.payments_ids = payments_ids

    async def start_validation(self):
        self.validation_amount = 1 + randint(1111, 9999) / 10_000
        return validation_view(self)

    async def save(self):
        data = {k: getattr(self, k) for k in self.__slots__}
        try:
            await write_file(f'wallets/pi/{self.id}.json', data)

        except Exception as e:
            print(f"Erreur lors de la sauvegarde de {self.user_id}: {e}")
    
    async def start_deposit(self, amount: int):
        deposit_amount = amount + randint(1111, 9999) / 100_000
        return deposit_view(self, deposit_amount)
    
    async def add_pi(self, amount: float):
        if amount < 0:
            raise ValueError("Le montant doit être positif")
        
        self.balance += amount
        await self.save()
    
    @staticmethod
    async def from_file(path: str):
        data = await read_file(path)
        return PiWallet(
            data.get('id'),
            data.get('verified', False),
            data.get("balance", 0),
            data.get("validation_amount"),
            data.get('payments_ids', [])
        )

    @staticmethod
    async def add_to_wallet(payment_id: int, amount: float):
        payments_ids: dict[str, str] = await read_file('wallets/pi_pending_payments.json')
        if payment_id in payments_ids:
            wallet = await PiWallet.from_file(f'{payments_ids[payment_id]}.json')
            await wallet.add_pi(amount)