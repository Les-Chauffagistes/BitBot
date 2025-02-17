class Operation:
    """Abstract class for BitStack operations"""

    __slots__ = ('date', 'fuseau', 'description', 'bitcoin_price', 'id')

    def __init__(self, date: str, fuseau: str, description: str, bitcoin_price: str, id: str):
        self.date = date
        self.fuseau = fuseau
        self.description = description
        self.bitcoin_price = bitcoin_price
        self.id = id

    def __repr__(self):
        return f"Operation <date={self.date} fuseau={self.fuseau} description={self.description} bitcoin_price={self.bitcoin_price} id={self.id}>"
