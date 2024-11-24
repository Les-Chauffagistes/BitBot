

from discord import User


class Item:
    def __init__(self, id: int, seller: User, name: str, description: str, price: int, buyer: User = None):