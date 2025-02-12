from discord import Embed, Interaction
from init import client, COLOR

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
    await send(interaction, "Pemission manquante", "Vous ne pouvez pas faire ça")

async def incomplete_signin_view(interaction: Interaction):
    await send(interaction, "Votre inscription n'est pas valide", f"Il manque certaines informations à votre profil avant de pouvoir faire ça. Rendez vous sur <#1247211754283601931> et saisissez les informations manquantes.")

async def item_not_found(interaction: Interaction):
    await send(interaction, "Objet introuvable", "Il a peut être été supprimé entre temps.")