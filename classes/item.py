import os
from typing import Literal, Optional
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

class AdminItem(BaseItem):
    """Représente un objet mis en vente par Fulcran"""

    __slots__ = BaseItem.__slots__ + ("__variantes__", "emoji", "published")

    class Variante(BaseItem):
        """Représente une variante de l'objet"""

        __slots__ = BaseItem.__slots__ + ('id', 'name', 'price', 'description', 'buyers', 'promo', 'item')

        def __init__(self, id, name, description, price: int, promo: int | None, buyers: list[int]):
            super().__init__(id, name, description, None, None)
            self.price = int(price)
            self.promo = int(promo) if promo else None
            self.buyers = buyers
            self.item: AdminItem

        def __eq__(self, other: 'AdminItem.Variante'):
            return self.id == other.id
    
        def __hash__(self):
            return hash(self.id)

        @property
        def json(self):
            return {
                "id": self.id,
                "name": self.name,
                "description": self.description,
                "price": int(self.price),
                "promo": int(self.promo) if self.promo else None,
                "buyers": self.buyers
            }

        @classmethod
        def from_dict(cls, data: dict[str, str | int | list[int]]):
            return AdminItem.Variante(**data)
    
        @property
        def user_price(self):
            if self.promo:
                return self.promo
            
            return self.price

    def __init__(self, id, name, description, channel_id, message_id, variantes: list[Variante], emoji: Optional[str], published: bool):
        super().__init__(id, name, description, channel_id, message_id)
        self.__variantes__ = variantes
        self.emoji = emoji
        self.published = published

    def get_variante(self, id: int):
        for variante in self.__variantes__:
            if variante.id == int(id):
                variante.item = self
                return variante

        else:
            log.warn("not found")
        
    async def delete_variante(self, id: int):
        for variante in self.__variantes__:
            if variante.id == id:
                self.__variantes__.remove(variante)
                await self.save()

    @property
    def min_price(self):
        if self.variantes:
            v = self.variantes[0]
            min_price = v.promo if v.promo else v.price

            for variante in self.variantes:
                if variante.promo:
                    if variante.promo < min_price:
                        min_price = variante.promo

                elif variante.price < min_price:
                    min_price = variante.price

            return min_price
        
    @property
    def channel(self):
        return client.get_channel(self.channel_id)

    @property
    async def message(self):
        try:
            return await fetch(self.channel_id, self.message_id)
    
        except:
            return None
    
    @property
    def variantes(self):
        return self.__variantes__

    @property
    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "channel_id": self.channel_id,
            "message_id": self.message_id,
            "variantes": [v.json for v in self.variantes],
            "emoji": self.emoji,
            "published": self.published
        }

    async def save(self):
        await write_file(f"business/shop/{self.id}.json", self.json)

    async def create_variante(self, id: int, name: str, description: str, price: int, promo: str):
        variante = self.Variante(id, name, description, price, int(promo) if len(promo) != 0 else None, [])
        variante.item = self
        self.__variantes__.append(variante)
        await self.save()
        return variante

    @classmethod
    async def from_id(cls, item_id: str | int):
        item_data = await read_file(f"business/shop/{item_id}.json")
        variantes = []
        for variante in item_data.get("variantes", []):
            variantes.append(AdminItem.Variante.from_dict(variante))
        item_data["variantes"] = variantes
        return AdminItem(**item_data)

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
            "fees": self.fees,
            "sell_type": self.sell_type,
            "is_paused": self.is_paused
        }
    
    @staticmethod
    async def from_id(id: int):
        if os.path.exists(f"data/business/sales/{id}.json"):
            data = await read_file(f"business/sales/{id}.json")
            return CommunityItem(**data)
        
        return None
    
    async def save(self):
        log.debug(self.json)
        await write_file(f"business/sales/{self.id}.json", self.json)