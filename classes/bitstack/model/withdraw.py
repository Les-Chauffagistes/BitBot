from classes.bitstack.model.operation import Operation

class Withdraw(Operation):
    """Represents a witdrawal operation """

    __slots__ = Operation.__slots__ + ('bitcoin_sent', 'bitcoin_price')

    def __init__(self, date: str, fuseau: str, bitcoin_sent: str, description: str, bitcoin_price: str, id: str):
        super().__init__(date, fuseau, description, bitcoin_price, id)
        self.bitcoin_sent = bitcoin_sent