import os
from random import randint
from typing import Optional
from discord import User
from functions.utils import read_file, write_file
from modules.pinet.classes import Wallet
from views.pi_wallet import deposit_view, validation_view
from init import log

class BaseDiscordWallet:
    __slots__ = ('id', 'badges', 'balance', 'validation_amount')

    def __init__(self, user_id: int, badges: list[str], balance: float, validation_amount: Optional[float]) -> None:
        self.id = user_id
        self.badges = badges
        self.balance = balance
        self.validation_amount = validation_amount

    async def save(self):
        raise NotImplementedError

    def start_validation(self):
        raise NotImplementedError

class PiWallet(BaseDiscordWallet):
    class BaseError(Exception):
        pass

    class FundsError(BaseError):
        pass

    __slots__ = BaseDiscordWallet.__slots__ + ('payments_ids', 'address', 'locale')

    def __init__(self, user_id: int, badges: bool, balance: float, address: str | None, validation_amount: Optional[float], payments_ids: list[int], locale: str):
        super().__init__(user_id, badges, balance, validation_amount)
        self.payments_ids = payments_ids
        self.address = address
        self.locale = locale

    async def start_validation(self):
        if not self.validation_amount:
            self.validation_amount = 1 + randint(1111, 9999) / 1_000_000
            await self.save()
            
        payments_ids: dict[str, str] = await read_file('wallets/pi_pending_payments.json')
        payments_ids[str(self.validation_amount)] = self.id
        await write_file('wallets/pi_pending_payments.json', payments_ids)

        return validation_view(self)

    async def send(self, amount: int, to: 'PiWallet'):
        if amount > 0:
            if self.balance >= amount:
                try:
                    self.balance -= amount
                    await self.save()
                
                except:
                    raise Exception
                
                to = await self.from_user(to.id)
                
                try:
                    await to.add_pi(amount)

                except:
                    self.balance += amount
                    await self.save()
                    raise Exception
            
            else:
                raise self.FundsError
        
        else:
            raise ValueError

    async def save(self):
        data = {k: getattr(self, k) for k in self.__slots__}
        try:
            await write_file(f'wallets/pi/{self.id}.json', data)

        except Exception as e:
            print(f"Erreur lors de la sauvegarde de {self.id}: {e}")
    
    async def start_deposit(self, amount: int):
        deposit_amount = amount + randint(1111, 9999) / 1_000_000
        payments_ids: dict[str, str] = await read_file('wallets/pi_pending_payments.json')
        payments_ids[str(deposit_amount)] = self.id
        await write_file('wallets/pi_pending_payments.json', payments_ids)
        return await deposit_view(self, deposit_amount)
    
    async def add_pi(self, amount: float):
        if amount < 0:
            raise ValueError("Le montant doit être positif")
        
        self.balance += amount
        await self.save()
        return self
    
    async def remove_pi(self, amount: float):
        if amount < 0:
            raise ValueError("Le montant doit être positif")

        if self.balance < amount:
            raise self.FundsError
        
        self.balance -= amount
        await self.save()
        return self
    
    @staticmethod
    async def create_new(for_user: User, address: Optional[str] = None, locale: Optional[str] = None):
        if await PiWallet.from_user(for_user.id):
            return
        
        await write_file(
            f'wallets/pi/{for_user.id}.json',
            {
                "id": for_user.id,
                "badges": [],
                "balance": 0,
                "address": address,
                "validation_amount": None,
                "payments_ids": [],
                "locale": locale
            }
        )
        return await PiWallet.from_file(f'wallets/pi/{for_user.id}.json')
    
    @staticmethod
    async def from_file(path: str):
        data = await read_file(path)
        return PiWallet(
            data.get('id'),
            data.get('badges', []),
            data.get("balance", 0),
            data.get('address'),
            data.get("validation_amount"),
            data.get('payments_ids', []),
            data.get('locale')
        )

    @staticmethod
    async def add_to_wallet(amount: float):
        #log.debug(f"Searching {amount}...")
        payments_ids: dict[str, str] = await read_file('wallets/pi_pending_payments.json')
        if str(amount) in payments_ids:
            wallet = await PiWallet.from_file(f'wallets/pi/{payments_ids[str(amount)]}.json')
            wallet = await wallet.add_pi(amount)
            del payments_ids[str(amount)]
            await write_file('wallets/pi_pending_payments.json', payments_ids)
            return wallet
        
        #log.debug('Not found')
        return None
    
    @staticmethod
    async def from_user(user_id: int):
        if os.path.exists(f"data/wallets/pi/{user_id}.json"):
            return await PiWallet.from_file(f"wallets/pi/{user_id}.json")
    
    @property
    def on_chain(self):
        return Wallet(self.address) if self.address else None
    
    async def verify(self):
        if "verified" not in self.badges:
            self.badges.append("verified")
            await self.save()
            return True
        
        await self.save()
        return False

    async def unverify(self):
        if "verified" in self.badges:
            self.badges.remove("verified")
            await self.save()
            return True
        
        await self.save()
        return False
    
    async def untrust(self):
        if "trusted" in self.badges:
            self.badges.remove("trusted")
            await self.save()
            return True
        
        await self.save()
        return False
    
    async def trust(self):
        if "trusted" not in self.badges:
            self.badges.append("trusted")
            await self.save()
            return True
        
        await self.save()
        return False

    @property
    def is_verified(self):
        return "verified" in self.badges

    @property
    def is_trusted(self):
        return "trusted" in self.badges