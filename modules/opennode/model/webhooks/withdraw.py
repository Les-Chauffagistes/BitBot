from typing import Literal, TypedDict


class lnurl(TypedDict):
    id: str
    external_id: str

class Withdraw(TypedDict):
    id: str
    callback_url: str
    type: Literal['ln']
    status: Literal['confirmed', 'failed']
    amount: int
    fee: int
    reference: str
    processed_at: int
    address: str
    custom_id: str
    hashed_order: str
    lnurl_withdrawal: str