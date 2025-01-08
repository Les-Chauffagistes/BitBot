from discord import Embed, Interaction, Member, Permissions
from discord.app_commands import Group

from classes.discord_wallet import PiWallet
from init import BADGE, COLOR

class CustomGroup(Group):
    pass

badge = CustomGroup(
    name = "badge",
    description = "Gestion des badges",
    default_permissions = Permissions(administrator = True)
)

@badge.command(
    name = "add",
    description = "Ajouter un badge à un utilisateur"
)
async def addCommand(interaction: Interaction, utilisateur: Member, badge: BADGE):
    wallet = await PiWallet.from_user(utilisateur.id)
    if wallet:
        match badge:
            case "Vérifié":
                r = await wallet.verify()
                
            case "Vendeur de confiance":
                r = await wallet.trust()
                
        if r:
            await interaction.response.send_message(
                embed = Embed(
                    title = "Badge ajouté",
                    description = f"L'utilisateur a réçu le badge {badge}",
                    color = COLOR
                ),
                ephemeral = True
            )
        
        else:
            await interaction.response.send_message(
                embed = Embed(
                    title = "Badge déjà acquis",
                    description = f"L'utilisateur a déjà le badge {badge}",
                    color = COLOR
                ),
                ephemeral = True
            )

@badge.command(
    name = "remove",
    description = "Retirer un badge à un utilisateur"
)
async def removeCommand(interaction: Interaction, utilisateur: Member, badge: BADGE):
    wallet = await PiWallet.from_user(utilisateur.id)
    if wallet:
        match badge:
            case "Vérifié":
                r = await wallet.unverify()
                
            case "Vendeur de confiance":
                r = await wallet.untrust()
                
        if r:
            await interaction.response.send_message(
                embed = Embed(
                    title = "Badge retiré",
                    description = f"L'utilisateur a perdu le badge {badge}",
                    color = COLOR
                ),
                ephemeral = True
            )
        
        else:
            await interaction.response.send_message(
                embed = Embed(
                    title = "Badge non acquis",
                    description = f"L'utilisateur n'a pas le badge {badge}",
                    color = COLOR
                ),
                ephemeral = True
            )