from typing import cast
from discord import Interaction
from classes.discord_wallet import BitcoinWallet
from functions.utils import read_file
from init import log

async def interact(interaction: Interaction, id: str, values: list[str]):
    user_wallet = await BitcoinWallet.from_user_id(interaction.user.id)
    args = id.split("#")
    del args[0]
    match id.split("#")[0]:
        case "LNURL":
            button_id = args[0]
            data = cast(dict[str, str], await read_file("wallets/bitcoin_lnurl_ids.json"))
            lnurl = data.get(button_id)
            if lnurl:
                await interaction.response.send_message(lnurl)
            

