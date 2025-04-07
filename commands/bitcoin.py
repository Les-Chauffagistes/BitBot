from math import ceil
import traceback
from typing import Literal, Optional
from discord.app_commands import Group, AppCommandContext, AppInstallationType, Range, describe
from discord import Embed, Interaction, User
from classes.discord_wallet import BitcoinWallet
from classes.emoji import Emoji
from init import COLOR, OPENNODE_CALLBACK_URL, log, storage
from modules import opennode
from views.bitcoin import payment_view, withdraw_view

class CustomGroup(Group):
    pass

bitcoin = CustomGroup(
    name = "bitcoin",
    description = "Commandes Bitcoin",
    allowed_contexts = AppCommandContext(
        guild = True,
        dm_channel = True,
        private_channel = True
    ),
    allowed_installs = AppInstallationType(
        guild = True,
        user = True
    )
)

@bitcoin.command(
    name = "deposit",
    description = "Deposer des bitcoins"
)
@describe(montant = "Montant à deposer", devise = "Dépot de Satoshi, ou équivalent en euro")
async def depositCommand(interaction: Interaction, montant: Range[int, 1, 10_000], devise: Literal["Euro", "Satoshi"]):
    try:
        if devise == "Euro":
            currency = "EUR"
        
        else:
            currency = None

        await interaction.response.send_message(
            embed = Embed(
                title = "Création d'un lien de paiement",
                description = f"{Emoji.loading} BitBot prépare votre invoice...",
                color = COLOR
            )
        )
        charge = await opennode.api.create_charge(montant, currency = currency, callback_url = OPENNODE_CALLBACK_URL.format(action = 'pay'), description = f"Payer en tant que {interaction.user.display_name}", customer_name = interaction.user.global_name, order_id = str(interaction.user.id))

        log.debug("Creating view")
        embed, view, file = await payment_view(charge)
        log.debug("end view")
        await interaction.edit_original_response(
            embed = embed,
            view = view,
            attachments = [file]
        )
    
    except:
        log.warn(traceback.format_exc())

@bitcoin.command(
    name = "withdraw",
    description = "Retirer des bitcoins"
)
async def withdrawCommand(interaction: Interaction, montant: Range[int, 1, 10_000], devise: Literal["Euro", "Satoshi"]):
    try:
        if devise == "Euro":
            if storage.bitcoin_price:
                montant = ceil((montant / storage.bitcoin_price) * 1e8)
        
        log.debug("montant:", montant)
        
        wallet = await BitcoinWallet.from_user_id(interaction.user.id)
        if wallet.balance < montant:
            await interaction.response.send_message(
                embed = Embed(
                    title = "Retrait impossible",
                    description = "Fonds insuffisants. Vous ne pouvez pas retirer une telle somme.",
                    color = COLOR
                )
            )
            return

        await interaction.response.send_message(
            embed = Embed(
                title = "Création d'un lien de paiement",
                description = f"{Emoji.loading} BitBot prépare votre invoice...",
                color = COLOR
            )
        )
        withdraw = await opennode.api.initiate_lnurl_withdrawal(
            min_amount = montant,
            max_amount = montant,
            callback_url = OPENNODE_CALLBACK_URL.format(action = 'withdraw'),
            external_id = str(interaction.user.id),
            description = f"Retirer en tant que {interaction.user.display_name}"
        )
        embed, view, file = await withdraw_view(withdraw)
        await interaction.edit_original_response(
            embed = embed,
            view = view,
            attachments = [file]
        )
        await wallet.remove_sat(montant)

    except:
        log.warn(traceback.format_exc())

@bitcoin.command(
    name = "wallet",
    description = "Afficher le solde de votre wallet"
)
async def walletCommand(interaction: Interaction):
    wallet = await BitcoinWallet.from_user_id(interaction.user.id)
    price = f"{round((wallet.balance / 1e8) * storage.bitcoin_price, 2):,}".replace(",", " ").replace(".", ",")

    await interaction.response.send_message(
        embed = Embed(
            title = "Wallet Lightning discord",
            description = f"# {wallet.balance} {Emoji.sat}",
            color = COLOR
        ).set_footer(
            text = f"Environ {price} €",
            icon_url = "https://registry.start9.com/package/v0/icon/mempool"
        )
    )

@bitcoin.command(
    name = "send",
    description = "Envoyer des bitcoins"
)
@describe(membre = "La personne qui doit recevoir", montant = "Montant à envoyer", devise = "Envoyer des satoshis, ou équivalent en euro. Satoshi par défaut", message = "Message facultatif à joindre")
async def sendCommand(interaction: Interaction, membre: User, montant: Range[int, 1, 10_000], devise: Literal["Euro", "Satoshi"] = "Satoshi", message: Optional[str] = None):
    assert interaction.client.user
    user_wallet = await BitcoinWallet.from_user_id(interaction.user.id)
    recipient_wallet = await BitcoinWallet.from_user_id(membre.id)
    if devise == "Euro":
        montant = ceil((montant / storage.bitcoin_price) * 1e8)

    try:
        await user_wallet.send(montant, recipient_wallet)
        try:
            await membre.send(
                embed = Embed(
                    title = "Vous avez reçu du Bitcoin",
                    description = f"{interaction.user.display_name} vous a envoyé {montant}{Emoji.sat}.\n{f'*{message}*' or ''}",
                    color = COLOR
                ).set_author(
                    name = interaction.user.display_name,
                    icon_url = interaction.user.display_avatar.url
                )
            )
            sent = True
        
        except:
            sent = False

        await interaction.response.send_message(
            embed = Embed(
                title = "Confirmation de transfert",
                description = f"Vous avez transféré {montant}{Emoji.sat} à {membre.display_name}\n{f"Note: {membre.display_name} n'a pas reçu de notification car il n'autorise pas {interaction.client.user.display_name} à lui envoyer des MP." if not sent else ''}",
                color = COLOR
            )
        )

    except AssertionError:
        await interaction.response.send_message(
            embed = Embed(
                title = "Échec de l'envoi",
                description = "Le montant saisi est invalide",
                color = COLOR
            )
        )
    
    except BitcoinWallet.FundsError:
        await interaction.response.send_message(
            embed = Embed(
                title = "Échec de l'envoi",
                description = "Vous n'avez pas assez de bitcoin pour réaliser ce transfert",
                color = COLOR
            )
        )
    
    finally:
        log.warn(traceback.format_exc())