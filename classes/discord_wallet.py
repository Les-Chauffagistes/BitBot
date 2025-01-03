from gettext import find
import os
from tabnanny import check
from typing import Literal, Optional
from discord import Embed, User
from classes.emoji import Emoji
from functions.utils import read_file, write_file
from modules.pinet.classes import Wallet
from views.pi_wallet import deposit_view, pay_buyer, pay_seller, validation_view
from init import ADMIN_NOTIFICATIONS_CHANNEL_ID, COLOR, GUILD_ID, log, client
from discord.ui import View, Button

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

    __slots__ = BaseDiscordWallet.__slots__ + ('payments_ids', 'address', 'locale', 'reason')

    def __init__(self, user_id: int, badges: bool, balance: float, address: str | None, validation_amount: Optional[float], payments_ids: list[int], locale: str, reason: Literal['deposit', 'seller', 'buyer']):
        super().__init__(user_id, badges, balance, validation_amount)
        self.payments_ids = payments_ids
        self.address = address
        self.locale = locale
        self.reason: Literal['deposit', 'seller', 'buyer'] = reason

    async def check_digits(self, digits: int):
        """Renvoie true si les digits sont disponibles, false sinon"""
        data: dict[str, int] = await read_file("wallets/pi_pending_payments.json")
        return not int(digits) in data.values()
    
    async def find_digits(self):
        d = 0
        digits = int(str(self.id)[-4:]) + d
        while not await self.check_digits(digits):
            d += 1
            digits = int(str(self.id)[-4:]) + d
        
        while digits < 1000:
            digits *= 10

        return digits

    async def start_validation(self):
        if not self.validation_amount:
            digits = await self.find_digits()
            self.validation_amount = 1 + digits / 1_000_000
            self.reason = "deposit"
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
        self.reason = "deposit"
        await self.save()
        deposit_amount = amount + await self.find_digits() / 1_000_000
        payments_ids: dict[str, str] = await read_file('wallets/pi_pending_payments.json')
        payments_ids[str(deposit_amount)] = self.id
        await write_file('wallets/pi_pending_payments.json', payments_ids)
        return await deposit_view(self, deposit_amount)

    async def start_withdrawal(self, amount: int):
        await self.remove_pi(amount)
        await client.get_channel(ADMIN_NOTIFICATIONS_CHANNEL_ID).send(
            embed = Embed(
                title = "Demande de retrait",
                description = f"L'utilisateur demande le retrait de **{amount} π** sur son wallet.\n```{self.address}```",
                color = COLOR
            ).set_author(
                name = client.get_guild(GUILD_ID).get_member(self.id).display_name,
                icon_url = client.get_guild(GUILD_ID).get_member(self.id).display_avatar.url
            ),
            view = View(timeout = None).add_item(
                Button(
                    label = "Marquer comme fait",
                    emoji = Emoji.done.value,
                    custom_id = f"CONFIRMWITHDRAWAL#{self.id}#{amount}"
                )
            )
        )
    
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
                "locale": locale,
                "reason": 'deposit'
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
            data.get('locale', ''),
            data.get('reason', 'deposit')
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
    
    async def become_seller(self):
        deposit_amount = 5 + await self.find_digits() / 1_000_000
        payments_ids: dict[str, str] = await read_file('wallets/pi_pending_payments.json')
        payments_ids[str(deposit_amount)] = self.id
        self.reason = 'seller'
        self.validation_amount = deposit_amount
        await write_file('wallets/pi_pending_payments.json', payments_ids)
        await self.save()
        return await pay_seller(self, deposit_amount)
    
    async def become_buyer(self):
        deposit_amount = 2 + await self.find_digits() / 1_000_000
        payments_ids: dict[str, str] = await read_file('wallets/pi_pending_payments.json')
        payments_ids[str(deposit_amount)] = self.id
        self.reason = 'buyer'
        self.validation_amount = deposit_amount
        await write_file('wallets/pi_pending_payments.json', payments_ids)
        await self.save()
        return await pay_buyer(self, deposit_amount)

    @property
    def is_verified(self):
        return "verified" in self.badges

    @property
    def is_trusted(self):
        return "trusted" in self.badges