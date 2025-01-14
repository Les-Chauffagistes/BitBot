from classes.commands import Command
from init import COLOR, client, tree
from discord import Embed, Interaction

@tree.command(
    name = "dm",
    description = "Ouvrir les mp de BitBot"
)
async def dmCommand(interaction: Interaction):
    try:
        msg = await interaction.user.send(
            embed = Embed(
                title = "Voici les mp de BitBot",
                description = f"Ici, vous pouvez utiliser les commandes suivantes:\n- {Command.ventes_add}\n- {Command.ventes_edit}",
                color = COLOR
            )
        )
        await interaction.response.send_message(
            embed = Embed(
                title = "BitBot vous a contacté en MP",
                description = f"Suivez ce lien pour accéder aux MP de BitBot: {msg.jump_url}",
                color = COLOR
            )
        )
    
    except:
        await interaction.response.send_message(
            embed = Embed(
                title = "Impossible d'envoyer le message",
                description = "Vous n'autorisez pas les messages de BitBot. Changez vos paramètres de confidentialité pour que BitBot puisse vous envoyer des messages privés.",
                color = COLOR
            ),
            ephemeral = True
        )