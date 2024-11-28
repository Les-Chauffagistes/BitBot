import os
from typing import Literal, Optional
from functions.utils import read_file, write_file
from init import client
from discord import Message


class Item:
    """Représente un objet mis en vente"""
    def __init__(self, id: int, name: str, description: str, price: int, seller_id: int, channel_id: Optional[int], message_id: Optional[int], buyer_id: Optional[int], payment_method: Literal['onchain', 'discord', 'any'], fees: Literal['included', 'euro', 'none']):
        self.id = id
        self.name = name
        self.description = description
        self.price = int(price)
        self.seller_id = seller_id
        self.channel_id = channel_id
        self.message_id = message_id
        self.buyer_id = buyer_id
        self.payment_method: Literal['onchain', 'discord', 'any'] = payment_method
        self.fees: Literal['included', 'euro', 'none'] = fees
    
    @property
    def channel(self):
        return client.get_channel(self.channel_id)
    
    @property
    async def message(self) -> Optional[Message]:
        try:
            return await self.channel.fetch_message(self.message_id)
        
        except:
            return None

    @property
    def seller(self):
        return client.get_user(self.seller_id)
    
    @property
    def buyer(self):
        return client.get_user(self.buyer_id) if self.seller_id else None
    
    @property
    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": int(self.price),
            "seller_id": self.seller_id,
            "channel_id": self.channel_id,
            "message_id": self.message_id,
            "buyer_id": self.buyer_id,
            "payment_method": self.payment_method,
            "fees": self.fees
        }
    
    @staticmethod
    async def from_id(id: int):
        if os.path.exists(f"data/business/sales/{id}.json"):
            data = await read_file(f"business/sales/{id}.json")
            return Item(**data)
        
        return None
    
    async def save(self):
        await write_file(f"business/sales/{self.id}.json", self.json)