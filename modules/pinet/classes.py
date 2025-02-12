from typing import Any, Literal, cast
from . import api
from datetime import datetime

from functions.utils import read_file, write_file

class Transaction:
    def __init__(self, data: dict[str, Any], wallet: 'Wallet', network: Literal['testnet', 'mainnet']):
        self.hash: str = data.get("hash", '')
        self.source = Wallet(data.get("source", ''))
        self.__network = network
        self.wallet = wallet
    
    @property
    def network(self):
        return cast(Literal['testnet', 'mainnet'], self.__network)
    
    async def is_blacklist(self) -> bool:
        return await Wallet.is_blacklisted(self)

    async def blacklist(self):
        return await Wallet.blacklist(self)
    
    @property
    async def payment(self):
        r = (await api.request(f"/transactions/{self.hash}/operations", 'get', self.network))
        return Payment(
            r.get("_embedded", {}).get("records", [])[0]
        )

class Payment:
    def __init__(self, data: dict[str, Any]):
        self.id = data.get("id")
        self.success: bool = data.get('transaction_successful', False)
        self.source = Wallet(data.get("source_account", ''))
        self.destination = Wallet(data.get("to", ''))
        self.amount = float(data.get("amount", 0))
        self.type: Literal['payment'] = data.get("type", 'payment')
        self.date = datetime.strptime(data.get('created_at', ''), "%Y-%m-%dT%H:%M:%SZ")
        self.hash: str = data.get("transaction_hash", '')
        self.asset: Literal['native'] = data.get("asset_type", 'native')
    
    async def is_blacklist(self) -> bool:
        return await Wallet.is_blacklisted(self)

    async def blacklist(self):
        return await Wallet.blacklist(self)
    
    async def is_notified(self):
        return await Wallet.is_notified(self)
    
    async def notify(self):
        return await Wallet.notify(self)
    
    def __repr__(self):
        return f'<{self.source.address[0:5]}...{self.source.address[-5:-1]} -> {self.amount} -> {self.destination.address[0:5]}...{self.destination.address[-5:-1]}>'

class Wallet:
    def __init__(self, address: str):
        self._address = address
    
    @property
    def address(self):
        return self._address.upper()
    
    async def get_testnet_balance(self) -> float:
        """Renvoie le montant en Pi Tesntet de l'utilisateur. Renvoie None si pas de wallet"""
        return float((await api.request(f'/accounts/{self.address}', 'get', 'testnet')).get("balances", [{}])[0].get("balance"))
    
    async def get_mainnet_balance(self) -> float:
        """Renvoie le montant en Pi Mainnet de l'utilisateur. Renvoie None si pas de wallet"""
        return float((await api.request(f'/accounts/{self.address}', 'get', 'mainnet')).get("balances", [{}])[0].get("balance"))
    
    async def get_mainnet_history(self, limit: int = 5) -> list[Transaction]:
        return [
            Transaction(payment, self, 'mainnet') for payment in (
                await api.request(
                    f'/accounts/{self.address}/transactions?limit={limit}&order=desc', 
                    'get',
                    'mainnet'
                )).get("_embedded", {}).get('records', [])
            ]
    
    async def get_testnet_history(self, limit: int = 5) -> list[Transaction]:
        return [
            Transaction(payment, self, 'testnet') for payment in (
                await api.request(
                    f'/accounts/{self.address}/transactions?limit={limit}&order=desc', 
                    'get',
                    'testnet'
                )).get("_embedded", {}).get('records', [])
            ]

    @staticmethod
    async def is_blacklisted(payment: Payment | Transaction) -> bool:
        blacklisted = cast(list[str], await read_file("wallets/pi_blacklist_payments.json"))
        return payment.hash in blacklisted
    
    @staticmethod
    async def blacklist(payment: Payment | Transaction):
        blacklisted = cast(list[str], await read_file("wallets/pi_blacklist_payments.json"))
        blacklisted.append(payment.hash)
        await write_file("wallets/pi_blacklist_payments.json", blacklisted)
    
    @staticmethod
    async def is_notified(payment: Payment | Transaction):
        notified = cast(list[str], await read_file("wallets/pi_notified_payments.json"))
        return payment.hash in notified
    
    @staticmethod
    async def notify(payment: Payment):
        notified = cast(list[str], await read_file("wallets/pi_notified_payments.json"))
        notified.append(payment.hash)
        await write_file("wallets/pi_notified_payments.json", notified)


wallet = Wallet('GC5NAVYCC7GYZO2LRTDJXJZFAWAGTKNHJBX43TN2RBMEOAUN37FMSEZD')