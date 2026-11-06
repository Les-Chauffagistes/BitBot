from discord import Embed, Interaction
from ..globals import COLOR


async def send(interaction: Interaction, title: str, description: str):
    await interaction.response.send_message(
        embed = Embed(
            title = title,
            description = description,
            color = COLOR
        ),
        ephemeral = True
    )


async def missing_permission(interaction: Interaction):
    await send(interaction, "Permission manquante", "Vous ne pouvez pas faire ça")
