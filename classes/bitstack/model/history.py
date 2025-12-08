from datetime import datetime
from classes.bitstack.model.operation import Operation
from classes.bitstack.model.deposit import Deposit
from classes.bitstack.model.exchange import Exchange

from aiohttp import ClientSession
from classes.bitstack.model.withdraw import Withdraw
import csv

class History:
    """BitStack operations history"""

    __slots__ = ('operations')

    def __init__(self, operations: list[Operation]):
        self.operations = operations

    @classmethod
    def from_csv(cls, path: str = "../data/tx.csv"):
        with open(path, 'r') as file:
            results: list[Operation] = []
            reader = csv.reader(file)
            next(reader)

            for row in reader:
                if row[0] == 'Échange':
                    results.append(Exchange(
                        date = row[1],
                        fuseau = row[2],
                        bitcoin_received = row[3],
                        fiat_sent = row[5],
                        fees = row[7],
                        description = row[9],
                        bitcoin_price = row[11],
                        id = row[15],
                    ))

                elif row[0] == 'Dépôt':
                    results.append(Deposit(
                        date = row[1],
                        fuseau = row[2],
                        bitcoin_received = row[3],
                        description = row[9],
                        bitcoin_price = row[11],
                        id = row[15],
                    ))
                
                elif row[0] == "Retrait":
                    results.append(Withdraw(
                        date = row[1],
                        fuseau = row[2],
                        bitcoin_sent = row[5],
                        description = row[9],
                        bitcoin_price = row[10],
                        id = row[15]
                    ))

                else:
                    print("Opération inconnue:", row[0])

            return cls(results)

    def __getitem__(self, index: int):
        return self.operations[index]

    def __iter__(self):
        return iter(self.operations)
    
    def __len__(self):
        return len(self.operations)
    
    @classmethod
    async def current_bitcoin_price(cls) -> int:
        async with ClientSession() as session:
            async with session.get('https://swakraft.fr/api/bitcoin-price') as response:
                response.raise_for_status()
                data = await response.json()
                return data['EUR']
    
    @property
    async def bitcoin_buyed(self) -> float:
        bitcoin_received = 0
        for operation in self.operations:
            if isinstance(operation, (Exchange, Deposit)):
                bitcoin_received += operation.bitcoin_received
        
        return bitcoin_received

    @property
    async def fiat_sent(self) -> float:
        fiat_sent = 0
        for operation in self.operations:
            if isinstance(operation, Exchange):
                fiat_sent += operation.fiat_sent
        
        return fiat_sent
    
    @property
    async def wallet_value(self) -> float:
        return await History.current_bitcoin_price() * await self.bitcoin_buyed
    
    @property
    def average_buy_price(self) -> float:
        prices: list[float] = []
        quantities: list[float] = []
        for operation in self.operations:
            if isinstance(operation, (Exchange, Deposit)):
                prices.append(operation.bitcoin_price)
                quantities.append(operation.bitcoin_received)

        return sum((prices[i] * quantities[i] for i in range(len(prices)))) / sum(quantities)

    @property
    async def instant_ROI(self):
        bitcoin_received = 0
        fiat_sent = 0
        for operation in self.operations:
            if isinstance(operation, Exchange):
                bitcoin_received += operation.bitcoin_received
                fiat_sent += operation.fiat_sent

            elif isinstance(operation, Deposit):
                bitcoin_received += operation.bitcoin_received
            
            elif isinstance(operation, Withdraw):
                pass
                
        return (bitcoin_received * await History.current_bitcoin_price()) / fiat_sent - 1
    
    @property
    def start_date(self) -> datetime: # type: ignore
        for operation in self.operations:
            if isinstance(operation, (Exchange, Deposit)):
                return datetime.fromisoformat(operation.date)
            
    @property
    def end_date(self) -> datetime: # type: ignore
        for operation in self.operations[::-1]:
            if isinstance(operation, (Exchange, Deposit)):
                return datetime.fromisoformat(operation.date)

    @property
    async def ROI(self):
        bitcoin_received = 0
        fiat_sent = 0
        last_bitcoin_price = 0
        for operation in self.operations:
            if isinstance(operation, Exchange):
                bitcoin_received += operation.bitcoin_received
                fiat_sent += operation.fiat_sent
                last_bitcoin_price = operation.bitcoin_price

            elif isinstance(operation, Deposit):
                bitcoin_received += operation.bitcoin_received
                last_bitcoin_price = operation.bitcoin_price
            
            elif isinstance(operation, Withdraw):
                pass
                
        return (bitcoin_received * last_bitcoin_price) / fiat_sent - 1
    