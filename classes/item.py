import os
from typing import Literal, Optional, cast
from functions.utils import fetch, read_file, write_file
from init import client
from discord import Message
from init import log

class BaseItem:

    __slots__ = ('id', 'name', 'description', 'channel_id', 'message_id')

    def __init__(self, id: int, name: str, description: str, channel_id: Optional[int], message_id: Optional[int]):
        self.id = id
        self.name = name
        self.description = description
        self.channel_id = channel_id
        self.message_id = message_id

class CommunityItem(BaseItem):
    """Représente un objet mis en vente par la communauté"""

    __slots__ = BaseItem.__slots__ + ('price', 'seller_id', 'buyer_id', 'payment_method', 'fees', 'sell_type', "is_paused")

    def __init__(self, id: int, name: str, description: str, price: int, seller_id: int, channel_id: Optional[int], message_id: Optional[int], buyer_id: Optional[int], payment_method: Literal['onchain', 'discord', 'any'], fees: Literal['included', 'euro', 'none'], sell_type: Literal['unique', 'multi'], is_paused: bool = False):
        super().__init__(id, name, description, channel_id, message_id)
        self.price = int(price)
        self.seller_id = seller_id
        self.buyer_id = buyer_id
        self.payment_method: Literal['onchain', 'discord', 'any'] = payment_method
        self.fees: Literal['included', 'euro', 'none'] = fees
        self.sell_type: Literal['unique', 'multi'] = sell_type
        self.is_paused: bool = is_paused
    
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
        return client.get_user(self.buyer_id) if self.buyer_id else None
    
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
            "fees": self.fees,
            "sell_type": self.sell_type,
            "is_paused": self.is_paused
        }
    
    class types:
        id: int
        name: str
        description: str
        price: int
        seller_id: int
        channel_id: Optional[int]
        message_id: Optional[int]
        buyer_id: Optional[int]
        payment_method: Literal['onchain', 'discord', 'any']
        fees: Literal['included', 'euro', 'none']
        sell_type: Literal['unique', 'multi']
        is_paused: bool
    
    @classmethod
    async def from_id(cls, id: int | str):
        if os.path.exists(f"data/business/sales/{id}.json"):
            data = cast(CommunityItem.types, await read_file(f"business/sales/{id}.json"))
            return cls(**data)
        
        return None
    
    async def save(self):
        log.debug(self.json)
        await write_file(f"business/sales/{self.id}.json", self.json)