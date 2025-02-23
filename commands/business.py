import traceback
from discord import Interaction
from discord.app_commands import Group, AppCommandContext
from classes.brand import Brand
from functions.utils import is_manager
from responses.default import missing_permission
from init import log
from views.admin_business import admin_brand_modal_edit, brand_main_admin, brand_main_edit

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
    name = "edit",
    description = "Modifier une enseigne ou une carte"
)
async def editCommand(interaction: Interaction):
    try:
        if is_manager(interaction.user):
            embed, view = await brand_main_admin()
            await interaction.response.send_message(
                embed = embed,
                view = view
            )
        
        else:
            await missing_permission(interaction)

    except:
        log.warn(traceback.format_exc())

@business.command(
    name = "add",
    description = "Ajouter une enseigne"
)
async def addCommand(interaction: Interaction):
    try:
        if is_manager(interaction.user):
            modal, raw_name, raw_description = admin_brand_modal_edit(None)
            async def handle_new_brand(interaction2: Interaction):
                try:
                    name = raw_name.value.strip()
                    description = raw_description.value.strip()
                    brand = Brand(interaction2.id, name, description)
                    await brand.save()
                    embed, view = await brand_main_edit(brand)
                    await interaction2.response.send_message(
                        embed = embed,
                        view = view
                    )
                
                except:
                    log.warn(traceback.format_exc())

            modal.on_submit = handle_new_brand
            await interaction.response.send_modal(modal)
        
        else:
            await missing_permission(interaction)

    except:
        log.warn(traceback.format_exc())