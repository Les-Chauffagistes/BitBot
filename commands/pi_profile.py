import traceback
from typing import Literal, Optional
from discord import ButtonStyle, Embed, File, Interaction, TextStyle, User
from discord.app_commands import Group
from classes.discord_wallet import PiWallet
from discord.ui import Modal, TextInput, View, Button
from discord.utils import MISSING
from classes.emoji import Emoji
from init import COLOR, log

class CustomgGroup(Group):
    pass

profile = CustomgGroup(
    name = "profile",
    description = "Votre profil Pi Network sur le serveur"
)

@profile.command(
    name = "edit",
    description = "Modifier votre profil Pi Network"
)
async def editCommand(interaction: Interaction):
    try:
        wallet = await PiWallet.from_user(interaction.user.id)
        modal = Modal(
            title = "Profil Pi"
        )
        raw_address = TextInput(
            label = "Adresse du wallet Pi Network",
            placeholder = "GABCDEFG...",
            min_length = 56,
            max_length = 56,
            required = False,
            default = wallet.address if wallet else None,
            style = TextStyle.long
        )
        raw_locale = TextInput(
            label = "Localisation approximative",
            placeholder = "Île de France",
            required = False,
            default = wallet.locale if wallet else None,
        )
        modal.add_item(raw_address).add_item(raw_locale)
        async def on_profile_update(interaction2: Interaction):
            try:
                if wallet:
                    wallet.locale = raw_locale.value.strip()
                    if (wallet.address != raw_address.value.strip()) and (raw_address.value.strip() != ""):
                        wallet.address = raw_address.value.strip()
                        await wallet.unverify()
                        embed, view = await wallet.start_validation()
                        await interaction2.response.send_message(
                            embed = embed,
                            view = view,
                            ephemeral = True
                        )

                    else:
                        await wallet.save()
                        if wallet.is_verified:
                            await interaction2.response.send_message(
                                embed = Embed(
                                    title = "Informations mises à jour",
                                    description = "Les informations de votre profil ont bien été mises à jour.",
                                    color = COLOR
                                )
                            )
                        
                        else:
                             await interaction2.response.send_message(
                                embed = Embed(
                                    title = "Informations mises à jour",
                                    description = f"Les informations de votre profil ont bien été mises à jour.\nSouhaitez vous reprendre la validation de votre profil ? Cela nous permet de vérifier que l'adresse commençant par {wallet.address[0:5]} est bien la votre. La vérification est requise pour acheter ou vendre sur ce serveur.",
                                    color = COLOR
                                ),
                                view = View(timeout = None).add_item(
                                    Button(
                                        label = "Reprendre la validation",
                                        custom_id = f"RESTART_VALIDATION#{interaction.user.id}",
                                        style = ButtonStyle.blurple,
                                        emoji = Emoji.verified_user.value
                                    )
                                )
                            )
                             
                else:
                    new_wallet = await PiWallet.create_new(interaction.user, raw_address.value.strip(), raw_locale.value.strip())
                    embed, view = await new_wallet.start_validation()
                    await interaction2.response.send_message(
                        embed = embed,
                        view = view,
                        ephemeral = True
                    )
                        
            except:
                log.warn(traceback.format_exc())

        modal.on_submit = on_profile_update
        await interaction.response.send_modal(modal)
    
    except:
        log.warn(traceback.format_exc())

@profile.command(
    name = "show",
    description = "Affiche un profil Pi Network"
)
async def showCommand(interaction: Interaction, membre: Optional[User]):
    try:
        if not membre:
            membre = interaction.user

        wallet = await PiWallet.from_user(membre.id)
        if wallet:
            if wallet.locale:
                await interaction.response.send_message(
                    embed = Embed(
                        title = "Profil Pi Network",
                        description = f"**Localisation:** {wallet.locale}",
                        color = COLOR
                    ).set_author(
                        name = membre.display_name,
                        icon_url = membre.display_avatar.url
                    ).set_footer(
                        text = "Vendeur de confiance" if wallet.is_trusted else "Vérifié" if wallet.is_verified else None,
                        icon_url = "attachment://trusted.png" if wallet.is_trusted else "attachment://verified.png" if wallet.is_verified else ""
                    ),
                    file = File("assets/trusted.png") if wallet.is_trusted else File("assets/verified.png") if wallet.is_verified else MISSING
                )
                return

        await interaction.response.send_message(
            embed = Embed(
                title = "C'est vide...",
                description = f"Le membre {membre.display_name} n'a pas préparé son profil Pi Network.",
                color = COLOR
            ).set_author(
                name = membre.display_name,
                icon_url = membre.display_avatar.url
            )
        )
    
    except:
        log.warn(traceback.format_exc())