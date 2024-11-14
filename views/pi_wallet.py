from typing import TYPE_CHECKING, Optional
from classes.emoji import Emoji
from init import WALLET_PI_FULCRAN
from views.init import *

if TYPE_CHECKING:
    from classes.discord_wallet import PiWallet

def validation_view(profile: PiWallet, back_id: Optional[str] = None):
    description = f"""
Pour utiliser votre profil Pi sur ce serveur, vous devez valider votre adresse Pi Network.
Envoyez **EXACTEMENT** {profile.validation_amount} Pi à l'adresse suivante :
```{WALLET_PI_FULCRAN}```
""".strip()
    embed = Embed(
        title = "Valider son profil Pi",
        description = description,
        color = COLOR
    )
    view = View()
    if back_id:
        view.add_item(
            Button(
                label = "Retour",
                custom_id = back_id.upper(),
                emoji = Emoji.back
            )
        )

    return embed, view

async def deposit_view(wallet: PiWallet, deposit_amount: float):
    wallet.validation_amount = deposit_amount
    await wallet.save()
    embed = Embed(
        title = "Déposer des Pis",
        description = f"Envoyez **EXACTEMENT** {deposit_amount} Pi à l'adresse suivante :\n```{WALLET_PI_FULCRAN}```",
        color = COLOR
    )

async def deposit_done(wallet: PiWallet, amount: float):
    if int(amount) == amount:
        amount = int(amount)
    
    display_amount = str(amount).replace('.', ',')
    embed = Embed(
        title = ""
    )