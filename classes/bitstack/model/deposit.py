from classes.bitstack.model.operation import Operation

class Deposit(Operation):
    """Represents a Deposit operation on BitStack"""

    __slots__ = Operation.__slots__ + ('bitcoin_received',)

    def __init__(self, date: str, fuseau: str, bitcoin_received: str, description: str, bitcoin_price: str, id: str):
        super().__init__(date, fuseau, description, bitcoin_price, id)
        self.bitcoin_received = float(bitcoin_received)