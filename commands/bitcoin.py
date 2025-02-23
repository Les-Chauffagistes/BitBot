from math import ceil
import traceback
from typing import Literal
from discord.app_commands import Group, AppCommandContext, AppInstallationType, Range, describe
from discord import Embed, Interaction
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