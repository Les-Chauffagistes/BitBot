from classes.bitstack.modele.operation import Operation

class Exchange(Operation):
    """Represents an Exchange operation on BitStack"""

    __slots__ = Operation.__slots__ + ('fees', 'fiat_sent', 'bitcoin_received')

    def __init__(self, date: str, fuseau: str, bitcoin_received: str, description: str, bitcoin_price: str, id: str, fees: str, fiat_sent: str):
        super().__init__(date, fuseau, description, bitcoin_price, id)
        self.fees = fees
        self.fiat_sent = fiat_sent
        self.bitcoin_received = bitcoin_received