from typing import Any, Literal, Optional
from aiohttp import ClientSession
from os import getenv
from dotenv import load_dotenv
from modules.opennode.model.withdraw_request import Withdraw_request
from .model.charge import Charge
from init import MODE

if not load_dotenv('data/.env'):
    load_dotenv("../../data/.env")

__ENDPOINT__ = 'https://api.opennode.com' if MODE == "PROD" else "https://dev-api.opennode.com"
WITHDRAW_API_KEY = getenv('OPEN_NODE_WITHDRAW_API_KEY_')
INVOICE_API_KEY = getenv('OPEN_NODE_WITHDRAW_API_KEY_')

assert (WITHDRAW_API_KEY and INVOICE_API_KEY)

_HEADERS_INVOICE = {
    "accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": INVOICE_API_KEY
}

_HEADERS_WITHDRAW = {
    "accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": WITHDRAW_API_KEY
}

async def make_request(
        *,
        url: str,
        method: Literal['get', 'post'],
        data: dict[str, Any],
        headers: dict[str, str]
    ) -> dict[str, Any] | list[Any]:
    async with ClientSession(__ENDPOINT__) as session:
        async with session.request(
            method,
            url,
            headers = headers,
            json = data
        ) as response:
            print(await response.text())
            response.raise_for_status()
            return await response.json()

async def create_charge(
        amount: int,
        callback_url: str,
        currency: Optional[Literal['EUR', 'USD']] = None,
        description: Optional[str] = None,
        customer_name: Optional[str] = None,
        customer_email: Optional[str] = None,
        order_id: Optional[str] = None,
    ):

    data = {key: value for key, value in locals().items() if value is not None and key != 'amount'}
    data['amount'] = amount
    print(data)
    
    data = await make_request(
        url = '/v1/charges',
        method = 'post',
        headers = _HEADERS_INVOICE,
        data = data
    )

    assert isinstance(data, dict)
    return Charge(data["data"])

async def initiate_lnurl_withdrawal(*, min_amount: int, max_amount: int, callback_url: str, external_id: str, description: str):
    data = await make_request(
        url = '/v2/lnurl-withdrawal',
        method = 'post',
        headers = _HEADERS_WITHDRAW,
        data = {
            "min_amt": min_amount,
            "max_amt": max_amount,
            "callback_url": callback_url,
            "external_id": external_id,
            "description": description
        }
    )
    print(data)

    assert isinstance(data, dict)
    return Withdraw_request(data["data"])