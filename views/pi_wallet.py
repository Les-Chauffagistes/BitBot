from typing import TYPE_CHECKING, Literal, Optional

from discord import File
from classes.emoji import Emoji
from init import WALLET_PI_FULCRAN, log
from views.init import *

if TYPE_CHECKING:
    from classes.discord_wallet import PiWallet

def validation_view(profile: 'PiWallet', back_id: Optional[str] = None):
    description = f"""
Pour utiliser votre profil Pi sur ce serveur, vous devez valider votre adresse Pi Network.
Envoyez **EXACTEMENT** {profile.validation_amount} Pi à l'adresse suivante :
```{WALLET_PI_FULCRAN}```
""".strip()
    embed = Embed(
        title = "Valider son profil Pi",
        description = description,
        color = COLOR
    ).set_footer(
        text = "Les Pi que vous enverrez ne seront pas perdus et seront transférés vers votre Wallet Pi Discord"
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

async def deposit_view(wallet: 'PiWallet', deposit_amount: float):
    wallet.validation_amount = deposit_amount
    wallet.reason = "deposit"
    await wallet.save()
    embed = Embed(
        title = "Déposer des Pi",
        description = f"Envoyez **EXACTEMENT** {deposit_amount} Pi à l'adresse suivante :\n```{WALLET_PI_FULCRAN}```",
        color = COLOR
    )
    return embed

async def wallet_view(wallet: 'PiWallet', network: Literal["Mainnet", "Testnet", "Discord"]):
    match network:
        case "Discord":
            embed = Embed(
                title = f"Wallet Pi Network - {network}",
                description = f"# {round(wallet.balance)} π",
                color = COLOR
            )
        
        case "Mainnet":
            balance = await wallet.on_chain.get_mainnet_balance()
            if balance != None:
                embed = Embed(
                    title = f"Wallet Pi Network - {network}",
                    description = f"# {balance} π",
                    color = COLOR
                )
                
            else:
                embed = Embed(
                    title = "Wallet introuvable",
                    description = f"Il n'y a pas de wallet {network} pour cette l'adresse commençant par {wallet.address[0:5]}.",
                    color = COLOR
                )

        case "Testnet":
            balance = await wallet.on_chain.get_testnet_balance()
            if balance != None:
                embed = Embed(
                    title = f"Wallet Pi Network - {network}",
                    description = f"# {balance} π",
                    color = COLOR
                )
                
            else:
                embed = Embed(
                    title = "Wallet introuvable",
                    description = f"Il n'y a pas de wallet {network} pour cette l'adresse commençant par {wallet.address[0:5]}.",
                    color = COLOR
                )
    
    embed.set_author(
        name = client.get_user(wallet.id).display_name,
        icon_url = client.get_user(wallet.id).display_avatar,
    ).set_image(
        url = "attachment://wallet.png"
    )
    return embed, File('assets/pi_wallet1.png', 'wallet.png')

async def pay_seller(wallet: 'PiWallet', deposit_amount: float):
    embed = Embed(
        title = "Payer l'inscription de vendeur",
        description = f"S'inscrire en tant que vendeur et bénéficier de tous les outils de vente du serveur coute 5 Pi. Pour payer, envoyez **EXACTEMENT** {deposit_amount} Pi à l'adresse suivante :\n```{WALLET_PI_FULCRAN}```",
        color = COLOR
    )
    return embed

async def pay_buyer(walelt: 'PiWallet', deposit_amount: float):
    embed = Embed(
        title = "Payer l'inscription d'acheteur",
        description = f"S'inscrire en tant qu'acheteur et acheter des produits sans frais sur le serveur coute 2 Pi. Pour payer, envoyez **EXACTEMENT** {deposit_amount} Pi à l'adresse suivante :\n```{WALLET_PI_FULCRAN}```",
        color = COLOR
    )
    return embed