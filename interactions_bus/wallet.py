import os
from discord import Embed, Interaction
from classes.discord_wallet import PiWallet
from discord.ui import View
from functions.utils import write_file
from init import COLOR

async def interact(interaction: Interaction, id: str, values: list[str]):
    user_wallet = await PiWallet.from_user(interaction.user.id)
    components = id.split("#")
    match components[0]:
        case "CRATEDCWALLET":
            wallet = PiWallet.create_new(interaction.user)
            if not wallet:
                await interaction.response.send_message(
                    embed = Embed(
                        title = "Votre wallet existe déjà",
                        description = "Vous avez déjà créé un wallet Pi Network sur Discord",
                        color = COLOR
                    )
                )
            
            else:
                await interaction.response.send_message(
                    embed = Embed(
                        title = "Votre wallet a été créé !",
                        description = "Vous pouvez désormais alimenter ce wallet et faire valider votre profil Pi Network",
                        color = COLOR
                    )
                )
        
        case "RESTART_VALIDATION":
            if int(components[-1]) == interaction.user.id:
                if not user_wallet.is_verified:
                    embed, view = await user_wallet.start_validation()
                    await interaction.response.send_message(
                        embed = embed,
                        view = view,
                        ephemeral = True
                    )
                
                else:
                    await interaction.response.edit_message(
                        embed = Embed(
                            title = "Informations mises à jour",
                            description = "Les informations de votre profil ont bien été mises à jour.",
                            color = COLOR
                        ),
                        view = View()
                    )