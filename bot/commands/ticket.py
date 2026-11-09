from discord.enums import ButtonStyle
from discord import TextChannel
from settings import settings
from discord import Interaction, Permissions
from discord.app_commands import Group
from discord import Embed
from ..globals import COLOR
from discord.ui import View, Button


class TicketGroup(Group):
    async def interaction_check(self, interaction: Interaction) -> bool:
        permissions = getattr(interaction.user, "guild_permissions", None)
        if permissions is None or not permissions.manage_guild:
            await interaction.response.send_message(
                "Vous n'avez pas la permission d'utiliser cette commande.",
                ephemeral = True
            )
            return False
        return True

tickets = TicketGroup(
    name = "tickets",
    description = "Ticket commands",
    default_permissions = Permissions(manage_guild=True),
    guild_only = True
)


@tickets.command(
    name = "close"
)
async def close_ticket(interaction: Interaction):
    if interaction.channel.category_id != settings.support_category_id or not isinstance(interaction.channel, TextChannel):
        await interaction.response.send_message(
            "Cette commande ne peut être utilisée que dans un ticket.",
            ephemeral = True
        )
        return

    await interaction.channel.edit(sync_permissions=True)
    await interaction.response.send_message(
        "Fermer le ticket ?",
        view = View(timeout=None).add_item(
            Button(
                label = "Fermer le ticket",
                style = ButtonStyle.danger,
                custom_id = "CLOSE_TICKET"
            )
        ),
        ephemeral=True
    )

@tickets.command(
    name = "spawn"
)
async def spawn_ticket(interaction: Interaction, channel: TextChannel):
    message = await channel.send(
        embed = Embed(
            title = "Contacter le support",
            description = "Pour contacter le support, veuillez créer un ticket en utilisant le bouton ci-dessous.",
            color = COLOR
        ),
        view = View(timeout=None).add_item(
            Button(
                label = "Créer un ticket",
                style = ButtonStyle.primary,
                custom_id = "CREATE_TICKET"
            )
        )
    )
    await interaction.response.send_message(message.jump_url, ephemeral=True)

@tickets.command(
    name = "delete"
)
async def delete_ticket(interaction: Interaction):
    if interaction.channel.category_id != settings.support_category_id or not isinstance(interaction.channel, TextChannel):
        await interaction.response.send_message(
            "Cette commande ne peut être utilisée que dans un ticket.",
            ephemeral = True
        )
        return

    await interaction.response.send_message(
        "Supprimer le ticket ?",
        view = View(timeout=None).add_item(
            Button(
                label = "Supprimer le ticket",
                style = ButtonStyle.danger,
                custom_id = "DELETE_TICKET"
            )
        ),
        ephemeral=True
    )