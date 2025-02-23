from datetime import datetime
from typing import Any, cast

from functions.utils import read_file, write_file


class Withdraw_request:
    """Represents a withdraw request for the user"""

    __slots__ = ('id', 'min_amt', 'max_amt', 'description', 'callback_url', 'external_id', 'uri', 'lnurl', 'created_at', 'expiry_date', 'used')

    def __init__(self, data: dict[str, Any]):
        self.id: str = data.get('id', '')
        self.min_amt: int = data.get('min_amt', 0)
        self.max_amt: int = data.get('max_amt', 0)
        self.description: str = data.get('description', '')
        self.callback_url: str = data.get('callback_url', '')
        self.external_id: str = data.get('external_id', '')
        self.uri: str = data.get('uri', '')
        self.lnurl: str = data.get('lnurl', '')
        self.created_at = datetime.fromisoformat(data.get('created_at', ''))
        self.expiry_date = datetime.fromisoformat(data.get('expiry_date', ''))
        self.used: bool = data.get('used', False)
    
    @property
    def json(self):
        return {
            'id': self.id,
            'min_amt': self.min_amt,
            'max_amt': self.max_amt,
            'description': self.description,
            'callback_url': self.callback_url,
            'external_id': self.external_id,
            'uri': self.uri,
            'lnurl': self.lnurl,
            'created_at': self.created_at.isoformat(),
            'expiry_date': self.expiry_date.isoformat(),
            'used': self.used
        }
    
    async def bind(self, button_id: str):
        data = cast(dict[str, str], await read_file("wallets/bitcoin_lnurl_ids.json"))
        data[button_id] = self.lnurl
        await write_file("wallets/bitcoin_lnurl_ids.json", data)