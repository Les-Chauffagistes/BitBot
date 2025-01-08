import os
from discord import ButtonStyle, Embed, Interaction, Message
from classes.emoji import Emoji
from classes.item import CommunityItem
from init import COLOR, tree
from discord.app_commands import default_permissions
from discord.ui import View, Button

@tree.context_menu(
    name = "Supprimer l'annonce",
)
@default_permissions(administrator = True)
async def supprimerContext(interaction: Interaction, message: Message):
    for file in os.listdir("data/business/sales"):
        item = await CommunityItem.from_id(file.removesuffix(".json"))
        msg = await item.message
        if msg:
            if msg.id == message.id:
                user_id = item.seller_id
                member = interaction.guild.get_member(user_id)
                if member:
                    display_name = member.display_name
                
                else:
                    display_name = "Utilisateur inconnu"

                await interaction.response.send_message(
                    embed = Embed(
                        title = f"Supprimer la vente de {display_name} ?",
                        description = "Cette action est irréversible",
                        color = COLOR
                    ),
                    view = View(timeout = None).add_item(
                        Button(
                            label = "Supprimer",
                            custom_id = f"ADMINDELETEITEM#{item.id}",
                            emoji = Emoji.delete.value,
                            style = ButtonStyle.danger
                        )
                    ).add_item(
                        Button(
                            label = "Supprimer et signaler",
                            custom_id = f"ADMINDELETEANDREPORT#{item.id}",
                            emoji = Emoji.report.value ,
                            style = ButtonStyle.danger
                        )
                    ),
                    ephemeral = True
                )
        
    else:
        await interaction.response.send_message(
            embed = Embed(
                title = "Suppression impossible",
                description = "Cette fonctionnalité permet uniquement de supprimer des ventes",
                color = COLOR
            ),
            ephemeral = True
        )