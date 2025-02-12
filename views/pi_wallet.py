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
                emoji = Emoji.back.value
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
        
        case "Mainnet" | "Testnet":
            if wallet.on_chain:
                try:
                    balance = await (wallet.on_chain.get_mainnet_balance() if network == "Mainnet" else wallet.on_chain.get_testnet_balance())
                    embed = Embed(
                        title = f"Wallet Pi Network - {network}",
                        description = f"# {balance} π",
                        color = COLOR
                    )
                    
                except:
                    embed = Embed(
                    title = "Wallet introuvable",
                    description = f"Il n'y a pas de wallet {network} pour l'adresse commençant par {wallet.on_chain.address[0:5]}.",
                    color = COLOR
                )   
                    
            else:
                embed = Embed(
                    title = "Wallet introuvable",
                    description = f"Il n'y a pas de wallet {network} pour cette adresse.",
                    color = COLOR
                )
    
    user = client.get_user(wallet.id)
    assert user
    embed.set_author(
        name = user.display_name,
        icon_url = user.display_avatar,
    ).set_image(
        url = "attachment://wallet.png"
    )
    return embed, File('assets/pi_wallet1.png', 'wallet.png')

async def pay_seller(wallet: 'PiWallet', deposit_amount: float, full_price: bool = True):
    if full_price:
        embed = Embed(
            title = "Payer l'inscription de vendeur",
            description = f"S'inscrire en tant que vendeur et bénéficier de tous les outils de vente du serveur coute 5 Pi. Pour payer, envoyez **EXACTEMENT** {deposit_amount} Pi à l'adresse suivante :\n```{WALLET_PI_FULCRAN}```",
            color = COLOR
        )
    
    else:
        embed = Embed(
            title = "Vous avez déjà payé les frais d'inscription",
            description = f"Nous avons besoin de vérifier l'adresse que vous avez fournie. Pour terminer l'inscription, envoyez **EXACTEMENT** {deposit_amount} Pi à l'adresse suivante :\n```{WALLET_PI_FULCRAN}```",
        )

    view = View(timeout = None).add_item(
        Button(
            label = "Obtenir le montant",
            custom_id = f"PRINT#{deposit_amount}"
        )
    ).add_item(
        Button(
            label = "Obtenir l'adresse",
            custom_id = f"PRINT#{WALLET_PI_FULCRAN}"
        )
    )
    return embed, view

async def pay_buyer(wallet: 'PiWallet', deposit_amount: float, full_price: bool = True):
    if full_price:
        embed = Embed(
            title = "Payer l'inscription d'acheteur",
            description = f"S'inscrire en tant qu'acheteur et acheter des produits sans frais sur le serveur coute 2 Pi. Pour payer, envoyez **EXACTEMENT** {deposit_amount} Pi à l'adresse suivante :\n```{WALLET_PI_FULCRAN}```",
            color = COLOR
        )

    else:
        embed = Embed(
            title = "Vous avez déjà payé les frais d'inscription",
            description = f"Nous avons besoin de vérifier l'adresse que vous avez fournie. Pour terminer l'inscription, envoyez **EXACTEMENT** {deposit_amount} Pi à l'adresse suivante :\n```{WALLET_PI_FULCRAN}```",
        )
        
    view = View(timeout = None).add_item(
        Button(
            label = "Obtenir le montant",
            custom_id = f"PRINT#{deposit_amount}"
        )
    ).add_item(
        Button(
            label = "Obtenir l'adresse",
            custom_id = f"PRINT#{WALLET_PI_FULCRAN}"
        )
    )
    return embed, view