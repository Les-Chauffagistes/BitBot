import traceback
from discord import Interaction
from discord.app_commands import Group, AppCommandContext
from discord.utils import MISSING
from classes.item import AdminItem
from functions.utils import is_manager
from responses.default import missing_permission
from views.admin_business import item_modal, item_view, main_edit_view
from init import log

class CustomGroup(Group):
    pass

business = CustomGroup(
    name = "business",
    description = "Commandes réservées aux admins pour la vente",
    allowed_contexts = AppCommandContext(
        guild = False,
        dm_channel = True
    )
)

@business.command(
    name = "add",
    description = "Ajouter un produit de vente générique"
)
async def addCommand(interaction: Interaction):
    try:
        if is_manager(interaction.user):
            modal, raw_title, raw_description = item_modal(None)
            async def on_item(interaction2: Interaction):
                try:
                    title = raw_title.value.strip()
                    description = raw_description.value.strip()
                    item = AdminItem(
                        interaction.id,
                        title,
                        description,
                        None,
                        None,
                        []
                    )
                    await item.save()
                    embed, view, file = await item_view(item) 
                    await interaction2.response.send_message(
                        embed = embed,
                        view = view,
                        file = file if file else MISSING
                    )
                except:
                    log.warn(traceback.format_exc())

            modal.on_submit = on_item
            await interaction.response.send_modal(modal)
        
        else:
            await missing_permission(interaction)
    
    except:
        log.warn(traceback.format_exc())

@business.command(
    name = "edit",
    description = "Modifier une boutique ou un article"
)
async def editCommand(interaction: Interaction):
    try:
        if is_manager(interaction.user):
            embed, view = await main_edit_view()
            await interaction.response.send_message(
                embed = embed,
                view = view
            )
        
        else:
            await missing_permission(interaction)
    
    except:
        log.warn(traceback.format_exc())