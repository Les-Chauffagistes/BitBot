import traceback
from discord import Embed, Interaction, TextStyle
from discord.app_commands import Group, AppCommandContext
from discord.ui import Modal, TextInput
from classes.item import Item
from functions.utils import is_seller
from views.community_business import item_edit, main_edit_view
from init import log
class CustomGroup(Group):
    pass

ventes = CustomGroup(
    name = "ventes",
    description = "Commandes de gestion des ventes de la communauté",
    allowed_contexts = AppCommandContext(
        guild = False,
        dm_channel = True
    )
)

@ventes.command(
    name = "add",
    description = "Ajouter un objet à vendre"
)
async def addCommand(interaction: Interaction):
    try:
        modal = Modal(title = "Fiche produit")
        raw_name = TextInput(
            label = "Nom du produit",
            placeholder = "Superbe boule de pétanque",
        )
        raw_description = TextInput(
            label = "Description du produit",
            placeholder = "Balle ronde et grise",
            style = TextStyle.long
        )
        raw_price = TextInput(
            label = "Prix de vente (Pi)",
            placeholder = "230"
        )
        modal.add_item(raw_name).add_item(raw_description).add_item(raw_price)
        async def on_product_update(interaction2: Interaction):
            product_id = interaction2.id
            item = Item(
                product_id,
                raw_name.value.strip(),
                raw_description.value.strip(),
                int(raw_price.value.strip()),
                interaction2.user.id,
                None,
                None,
                None,
                'any',
                'euro'
            )
            await item.save()
            embed, view, file = await item_edit(interaction2, item)
            await interaction2.response.send_message(
                embed = embed,
                view = view,
                file = file,
            )

        modal.on_submit = on_product_update
        await interaction.response.send_modal(modal)

    except:
        log.warn(traceback.format_exc())

@ventes.command(
    name = "edit",
    description = "Modifier un produit de vente"
)
async def editCommand(interaction: Interaction):
    try:
        if is_seller(interaction.user):
            embed, view = await main_edit_view(interaction.user)
            await interaction.response.send_message(
                embed = embed,
                view = view
            )

    except:
        log.warn(traceback.format_exc())