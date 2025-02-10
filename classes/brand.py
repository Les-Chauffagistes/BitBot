import os
from typing import Literal, Optional, cast
from discord import SelectOption
from typing import TypedDict
from functions.utils import read_file, write_file

class Brand:
    """Représente une enseigne"""

    __slots__ = ('id', 'name', 'description', 'cards')

    class Card:
        """Représente une carte de l'enseigne"""

        __slots__ = ('id', 'name', 'value', 'price', 'promo_price', '_codes', 'brand')

        def __init__(self, id: int, name: str, value: int, price: int, promo_price: Optional[int], codes: list[str]):
            self.id = id
            self.name = name
            self.value = value
            self.price = price
            self.promo_price = promo_price
            self._codes = codes
            self.brand: Brand

        async def remove_code(self, code: str):
            if code in self.codes:
                del self._codes[self._codes.index(code)]
                await self.brand.save()
            
            else:
                for current_code in self._codes:
                    if current_code.lower() == code.lower():
                        del self._codes[self._codes.index(current_code)]
                        await self.brand.save()
                        break
                
                else:
                    raise Brand.CardError("Code not found")

        async def add_code(self, code: str):
            for current_code in self.codes:
                if code.lower() == current_code.lower():
                    raise Brand.CardError("Code already exists")
            
            else:
                self._codes.append(code)
                await self.brand.save()
        
        async def drop_code(self):
            if self._codes:
                code = self._codes.pop(0)
                await self.brand.save()
                return code

        
        @property
        def codes(self) -> list[str]:
            return self._codes.copy()

        class types(TypedDict):
            """Card Types"""
            id: int
            name: str
            value: int
            price: int
            promo_price: Optional[int]
            codes: list[str]
        
        async def edit(self, name: Optional[str] = None, value: Optional[int] = None, price: Optional[int] = None, promo_price: Optional[int] = None):
            if name: self.name = name
            if value: self.value = value
            if price: self.price = price
            if promo_price: self.promo_price = promo_price
            await self.brand.save()

        @property
        def current_price(self) -> int:
            return self.promo_price if self.promo_price else self.price
        
        def json(self) -> dict[str, str | int | list[str] | None]:
            return {
                "id": self.id,
                "name": self.name,
                "value": self.value,
                "price": self.price,
                "promo_price": self.promo_price,
                "codes": self.codes
            }
 
    class CardError(Exception):
        def __init__(self, *args):
            super().__init__(*args)

    class types(TypedDict):
        """Brand Types"""
        id: int
        name: str
        description: str
        cards: list['Brand.Card.types']

    def __init__(self, id: int, name: str, description: str, cards: Optional[list[Card]] = None):
        self.id = id
        self.name = name
        self.description = description
        self.cards: list[Brand.Card] = cards if cards else []
    
    def json(self) -> dict[str, str | int | list[dict[str, str | int | list[str] | None]]]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "cards": [item.json() for item in self.cards]
        }
    
    def get_card(self, id: int) -> Optional['Brand.Card']:
        for card in self.cards:
            if card.id == id:
                return card
    
    @property
    def start_price(self) -> int:
        if not self.cards: raise self.CardError("No cards")
        min_price = self.cards[0].current_price
        for card in self.cards:
            if card.current_price < min_price:
                min_price = card.current_price

        return min_price

    async def save(self):
        await write_file(f"business/shop/{self.id}.json", self.json())
    
    async def add_card(self, id: int, name: str, value: int, price: int, promo_price: Optional[int]) -> Card:
        self.cards.append(Brand.Card(id, name, value, price, promo_price, []))
        await self.save()
        return self.cards[-1]

    @classmethod
    async def from_id(cls, id: int):
        data = cast(Brand.types, await read_file(f"business/shop/{id}.json"))
        brand = cls(
            data.get('id', 0),
            data.get('name', ''),
            data.get('description', '')
        )
        for raw_card in data.get('cards', []):
            card = Brand.Card(**raw_card)
            card.brand = brand
            brand.cards.append(card)
        
        return brand

    @classmethod
    async def select_all_brands(cls, selected_brand_id: Optional[int] = None) -> list[SelectOption]:
        options: list[SelectOption] = []
        for file in os.listdir("data/business/shop"):
            brand = await cls.from_id(int(file.split('.')[0]))
            options.append(
                SelectOption(
                    label = brand.name,
                    description = brand.description,
                    value = str(brand.id),
                    default = brand.id == selected_brand_id
                )
            )
        
        return options
    
    def select_all_cards(self, selected_card_id: Optional[int] = None) -> list[SelectOption]:
        return [
            SelectOption(
                label = card.name,
                description = f"{card.current_price} π",
                value = str(card.id),
                default = card.id == selected_card_id
            )
            for card in self.cards
        ]