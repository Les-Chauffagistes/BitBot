from datetime import datetime, timedelta
from typing import Any, Literal, Optional, TypedDict, cast

from functions.utils import read_file, write_file


class Charge:
    """Represents a charge on OpenNode"""

    __slots__ = (
        "id",
        "description",
        "desc_hash",
        "created_at",
        "status",
        "amount",
        "callback_url",
        "success_url",
        "hosted_checkout_url",
        "order_id",
        "currency",
        "source_fiat_value",
        "fiat_value",
        "auto_settle",
        "notif_email",
        "address",
        "metadata",
        "chain_invoice",
        "uri",
        "ttl",
        "payreq",
        "expires_at"
    )

    class lightning_invoice_data(TypedDict):
        expires_at: int
        payreq: str

    def __init__(self, data: dict[str, Any]):
        self.id: str = data.get("id", "")
        self.description: str = data.get("description", "")
        self.desc_hash: bool = data.get("desc_hash", False)
        self.created_at = datetime.fromtimestamp(data.get("created_at", 0))
        self.status = cast(Literal["paid", "unpaid", "expired"], data.get("status", "unpaid"))
        self.amount: int = data.get("amount", 0)
        self.callback_url: Optional[str] = data.get("callback_url")
        self.success_url: Optional[str] = data.get("success_url")
        self.hosted_checkout_url: str = data.get("hosted_checkout_url", '')
        self.order_id: Optional[str] = data.get("order_id")
        self.currency = cast(Literal['BTC'], data.get("currency"))
        self.source_fiat_value: int = data.get("source_fiat_value", 0)
        self.fiat_value: float = data.get("fiat_value", 0)
        self.auto_settle = cast(Literal[False], data.get("auto_settle"))
        self.notif_email: Optional[str] = data.get("notif_email")
        self.address: str = data.get("address", "")
        self.metadata: dict = data.get("metadata", {})
        self.chain_invoice: dict[str, str] = data.get('chain_invoice', {})
        self.uri: str = data.get('uri', '')
        self.ttl = timedelta(seconds = data.get('ttl', 0))
        self.payreq: str = data.get('lightning_invoice', {}).get('payreq', '')
        self.expires_at = datetime.fromtimestamp(data.get('lightning_invoice', {}).get('expires_at', 0))

    async def bind(self, button_id: str):
        data = cast(dict[str, str], await read_file("wallets/bitcoin_lnurl_ids.json"))
        data[button_id] = self.payreq
        await write_file("wallets/bitcoin_lnurl_ids.json", data)