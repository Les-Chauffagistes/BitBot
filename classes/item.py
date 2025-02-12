import os
from typing import Literal, Optional, TypedDict, cast
from functions.utils import fetch, read_file, write_file
from init import client
from discord import Message, TextChannel
from init import log

class CommunityItem:
    """Représente un objet mis en vente par la communauté"""

    __slots__ = ('__id', '__name', '__description', '__channel_id', '__message_id', '__price', '__seller_id', '__buyer_id', '__payment_method', '__fees', '__sell_type', "__is_paused")

    class types(TypedDict):
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

    payment_method_types = Literal['onchain', 'discord', 'any']
    fees_type = Literal['included', 'euro', 'none']
    sell_type_types = Literal['unique', 'multi']
    
    def __init__(
            self,
            id: int,
            name: str,
            description: str,
            price: int,
            seller_id: int,
            channel_id: Optional[int],
            message_id: Optional[int],
            buyer_id: Optional[int],
            payment_method: payment_method_types,
            fees: fees_type,
            sell_type: sell_type_types,
            is_paused: bool = False
        ):
        self.__id = id
        self.__name = name
        self.__description = description
        self.__channel_id = channel_id
        self.__message_id = message_id
        self.__price = int(price)
        self.__seller_id = seller_id
        self.__buyer_id = buyer_id
        self.__payment_method: CommunityItem.payment_method_types = payment_method
        self.__fees: CommunityItem.fees_type = fees
        self.__sell_type: CommunityItem.sell_type_types = sell_type
        self.__is_paused = is_paused

    @property
    def id(self):
        return self.__id
    
    @property
    def name(self):
        return self.__name
    
    @property
    def description(self):
        return self.__description
    
    @property
    def price(self):
        return int(self.__price)
    
    @property
    def channel_id(self):
        return self.__channel_id
    
    @property
    def message_id(self):
        return self.__message_id
    
    @property
    def seller_id(self):
        return self.__seller_id
    
    @property
    def buyer_id(self):
        return self.__buyer_id
    
    @property
    def payment_method(self):
        return self.__payment_method
    
    @property
    def fees(self):
        return self.__fees
    
    @property
    def sell_type(self):
        return self.__sell_type
    
    @property
    def is_paused(self):
        return self.__is_paused
    
    @name.setter
    def name(self, value: str):
        self.__name = value

    @description.setter
    def description(self, value: str):
        self.__description = value
    
    @channel_id.setter
    def channel_id(self, id: int):
        self.__channel_id = id
    
    @message_id.setter
    def message_id(self, id: int):
        self.__message_id = id

    @price.setter
    def price(self, value: int):
        self.__price = int(value)

    @seller_id.setter
    def seller_id(self, id: int):
        self.__seller_id = id
    
    @buyer_id.setter
    def buyer_id(self, id: int):
        self.__buyer_id = id

    @payment_method.setter
    def payment_method(self, method: payment_method_types):
        self.__payment_method = method

    @fees.setter
    def fees(self, fees: fees_type):
        self.__fees = fees
    
    @sell_type.setter
    def sell_type(self, type: sell_type_types):
        self.__sell_type = type
    
    @is_paused.setter
    def is_paused(self, status: bool):
        self.__is_paused = status
    
    @property
    def channel(self) -> TextChannel | None:
        return cast(TextChannel, client.get_channel(self.channel_id)) if self.channel_id else None
    
    @property
    async def message(self) -> Optional[Message]:
        if self.channel and self.message_id:
            return await self.channel.fetch_message(self.message_id)

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
    
    @classmethod
    async def from_id(cls, id: int | str):
        if os.path.exists(f"data/business/sales/{id}.json"):
            data = cast(CommunityItem.types, await read_file(f"business/sales/{id}.json"))
            return cls(**data)
        
        return None
    
    async def save(self):
        log.debug(self.json)
        await write_file(f"business/sales/{self.id}.json", self.json)