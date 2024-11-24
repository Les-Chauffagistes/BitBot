import os
from typing import Optional
from functions.utils import read_file, write_file
from init import client
from discord import Message


class Item:
    """Représente un objet mis en vente"""
    def __init__(self, id: int, name: str, description: str, price: int, seller_id: int, channel_id: Optional[int], message_id: Optional[int], buyer_id: Optional[int]):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.seller_id = seller_id
        self.channel_id = channel_id
        self.message_id = message_id
        self.buyer_id = buyer_id
    
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
            "price": self.price,
            "seller_id": self.seller_id,
            "channel_id": self.channel_id,
            "message_id": self.message_id,
            "buyer_id": self.buyer_id
        }
    
    @staticmethod
    async def from_id(id: int):
        if os.path.exists(f"data/business/sales/{id}.json"):
            data = await read_file(f"business/sales/{id}.json")
            return Item(**data)
        
        return None
    
    async def save(self):
        await write_file(f"business/sales/{self.id}.json", self.json)