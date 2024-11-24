from typing import Literal
from . import api
from datetime import datetime

from functions.utils import read_file, write_file

class Payment:
    def __init__(self, data: dict, wallet: 'Wallet'):
        self.id = data.get("id")
        self.success: bool = data.get('transaction_successful')
        self.source = Wallet(data.get("source_account"))
        self.destination = Wallet(data.get("to"))
        self.amount = float(data.get("amount"))
        self.type: Literal['payment'] = data.get("type")
        self.date = datetime.strptime(data.get('created_at'), "%Y-%m-%dT%H:%M:%SZ")
        self.hash: str = data.get("transaction_hash")
        self.asset: Literal['native'] = data.get("asset_type")
        self.wallet = wallet
    
    async def is_blacklist(self) -> bool:
        return await Wallet.is_blacklisted(self)

    async def blacklist(self):
        return await Wallet.blacklist(self)
    
    def __repr__(self):
        return f'<{self.source.address[0:5]}...{self.source.address[-5:-1]} -> {self.amount} -> {self.destination.address[0:5]}...{self.destination.address[-5:-1]}>'

class Wallet:
    def __init__(self, address: str):
        self.address = address
    
    async def get_testnet_balance(self) -> float:
        """Renvoie le montant en Pi Tesntet de l'utilisateur. Renvoie None si pas de wallet"""
        return float((await api.request(f'/accounts/{self.address}', 'get', 'testnet')).get("balances", [{}])[0].get("balance"))
    
    async def get_mainnet_balance(self) -> float:
        """Renvoie le montant en Pi Mainnet de l'utilisateur. Renvoie None si pas de wallet"""
        return float((await api.request(f'/accounts/{self.address}', 'get', 'mainnet')).get("balances", [{}])[0].get("balance"))
    
    async def get_mainnet_history(self, limit: int = 10) -> list[Payment]:
        return [
            Payment(payment, self) for payment in (
                await api.request(
                    f'/accounts/{self.address}/payments?limit={limit}&order=desc', 
                    'get',
                    'mainnet'
                )).get("_embedded", {}).get('records', [])
            ]
    
    async def get_testnet_history(self, limit: int = 10) -> list[Payment]:
        return [
            Payment(payment, self) for payment in (
                await api.request(
                    f'/accounts/{self.address}/payments?limit={limit}&order=desc', 
                    'get',
                    'testnet'
                )).get("_embedded", {}).get('records', [])
            ]

    async def is_blacklisted(payment: Payment) -> bool:
        blacklisted: list[str] = await read_file("wallets/pi_blacklist_payments.json")
        return payment.hash in blacklisted
    
    async def blacklist(payment: Payment):
        blacklisted: list[str] = await read_file("wallets/pi_blacklist_payments.json")
        blacklisted.append(payment.hash)
        await write_file("wallets/pi_blacklist_payments.json", blacklisted)


wallet = Wallet('GC5NAVYCC7GYZO2LRTDJXJZFAWAGTKNHJBX43TN2RBMEOAUN37FMSEZD')