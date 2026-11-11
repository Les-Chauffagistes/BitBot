from discord.abc import GuildChannel
from discord.enums import ButtonStyle
from discord import TextChannel, Member, CategoryChannel
from settings import settings
from discord import Interaction, Permissions
from discord.app_commands import Group
from discord import Embed
from ..globals import COLOR
from discord.ui import View, Button
from ..utils import create_ticket as make_ticket, is_ticket


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
    assert isinstance(interaction.channel, GuildChannel)
    if not is_ticket(interaction.channel):
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
    assert isinstance(interaction.channel, GuildChannel)
    if not is_ticket(interaction.channel):
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

@tickets.command(
    name = "create"
)
async def create_ticket(interaction: Interaction, membre: Member):
    assert interaction.guild is not None
    assert isinstance(interaction.user, Member)
    channel = interaction.guild.get_channel(settings.support_category_id)
    if not isinstance(channel, CategoryChannel):
        await interaction.response.send_message(
            "Impossible de créer le ticket à cause d'une erreur technique.",
            ephemeral = True
        )
        return

    ticket = await make_ticket(
        membre,
        channel,
        "admin",
        interaction.user
    )
    await interaction.response.send_message(
        f"Ticket créé: {ticket.jump_url}",
        ephemeral = True
    )
