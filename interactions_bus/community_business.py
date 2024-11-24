import os
from asyncio import sleep
import traceback
from typing import Literal
from discord import ButtonStyle, Embed, Interaction, TextStyle
from classes.commands import Command
from classes.discord_wallet import PiWallet
from discord.ui import View, Modal, TextInput, Button
from classes.emoji import Emoji
from classes.item import Item
from functions.utils import write_file
from init import COLOR, MODE, log
from responses import default
from views.community_business import item_edit, wallet_creation_view, wallet_payment_view

async def interact(interaction: Interaction, id: str, values: list[str]):
    user_wallet = await PiWallet.from_user(interaction.user.id)
    components = id.split("#")
    match components[0]:
        case "BECOME_BUYER":
            embed, view = await wallet_creation_view(interaction, user_wallet, 'acheteur')
            await interaction.response.send_message(
                embed = embed,
                view = view,
                ephemeral = True
            )
        
        case "BECOME_SELLER":
            embed, view = await wallet_creation_view(interaction, user_wallet, 'vendeur')
            await interaction.response.send_message(
                embed = embed,
                view = view,
                ephemeral = True
            )
        
        case "CREATESILENTWALLET" | "UPDATE_PROFILE":
            wallet = await PiWallet.from_user(interaction.user.id)
            if not wallet:
                wallet = await PiWallet.create_new(interaction.user)

            try:
                wallet = await PiWallet.from_user(interaction.user.id)
                modal = Modal(
                    title = "Confirmer votre profil"
                )
                raw_address = TextInput(
                    label = "Adresse de votre wallet Pi Network",
                    placeholder = "GABCDEFG...",
                    min_length = 56,
                    max_length = 56,
                    required = True,
                    default = wallet.address if wallet else None,
                    style = TextStyle.long
                )
                raw_locale = TextInput(
                    label = "Localisation approximative",
                    placeholder = "Île de France",
                    required = True,
                    default = wallet.locale if wallet else None,
                )
                modal.add_item(raw_address).add_item(raw_locale)
                async def on_profile_update(interaction2: Interaction):
                    try:
                        wallet.locale = raw_locale.value.strip()
                        if wallet.address != raw_address.value.strip() or not wallet.is_verified:
                            wallet.address = raw_address.value.strip()
                            await wallet.unverify()
                            embed, view = await wallet.start_validation()
                            embed.title = f"Devenir {components[1]} - Étape 2/3"
                            await interaction2.response.edit_message(
                                embed = embed,
                                view = view,
                            )
                            while True:
                                await sleep(1)
                                if (await PiWallet.from_user(interaction2.user.id)).is_verified:
                                    break
                                
                                else:
                                    log.debug('no')
                            
                            log.info('Verified')
                            embed, view = await wallet_payment_view(interaction2, user_wallet, components[1])
                            await interaction2.edit_original_response(
                                embed = embed,
                                view = view
                            )
                        
                        else:
                            await wallet.save()
                            embed, view = await wallet_payment_view(interaction2, user_wallet, components[1])
                            await interaction2.response.edit_message(
                                embed = embed,
                                view = view
                            )
                                
                    except:
                        log.warn(traceback.format_exc())

                modal.on_submit = on_profile_update
                await interaction.response.send_modal(modal)
            
            except:
                log.warn(traceback.format_exc())
        
        case "PAY_INSCRIPTION":
            role: Literal['acheteur', 'vendeur'] = components[1]
            if interaction.user.id == int(components[-1]):
                if MODE == "DEV":
                    role_buyer = interaction.guild.get_role(1310271143168573450)
                    role_seller = interaction.guild.get_role(1310271119466565755)
                
                else:
                    pass
                
                if role == 'acheteur':
                    discord_role = role_buyer
                
                else:
                    discord_role = (role_seller, role_buyer)

                if discord_role in interaction.user.roles:
                    await interaction.response.edit_message(
                        embed = Embed(
                            title = "Inscription déjà validée",
                            description = f"Vous disposez déjà des privilèges liés au rôle {role}.",
                            color = COLOR
                        ),
                        view = View()
                    )
                
                else:
                    try:
                        await user_wallet.remove_pi(2 if role == 'acheteur' else 5)
                    
                    except:
                        await interaction.response.send_message(
                            embed = Embed(
                                title = "Fonds insuffisants",
                                description = f"Utilisez la commande {Command.pi_deposit} pour déposer des Pi sur votre wallet.",
                                color = COLOR
                            ),
                            ephemeral = True
                        )
                        return
                    
                    await interaction.user.add_roles(*discord_role)
                    await interaction.response.edit_message(
                        embed = Embed(
                            title = "Inscription validée",
                            description = f"Vous avez obtenu tous les privilèges liés au rôle {role}.",
                            color = COLOR
                        ),
                        view = View()
                    )
                            
        case "EDITITEM":
            product_id = int(components[-1])
            item = await Item.from_id(product_id)
            modal = Modal(title = "Fiche produit")
            raw_name = TextInput(
                label = "Nom du produit",
                placeholder = "Superbe boule de pétanque",
                default = item.name
            )
            raw_description = TextInput(
                label = "Description du produit",
                placeholder = "Balle ronde et grise",
                style = TextStyle.long,
                default = item.description
            )
            raw_price = TextInput(
                label = "Prix de vente (Pi)",
                placeholder = "230",
                default = item.price
            )
            modal.add_item(raw_name).add_item(raw_description).add_item(raw_price)
            async def on_product_update(interaction2: Interaction):
                
                item = await Item.from_id(product_id)
                item.name = raw_name.value.strip()
                item.price = raw_price.value.strip()
                item.description = raw_description.value.strip()
                await item.save()
                embed, view = await item_edit(interaction2, item)
                await interaction2.response.edit_message(
                    embed = embed,
                    view = view
                )
            
            modal.on_submit = on_product_update
            await interaction.response.send_modal(modal)
        
        case "ADDITEMIMAGE":
            product_id = int(components[-1])
            item = await Item.from_id(product_id)
            await interaction.response.edit_message(
                embed = Embed(
                    title = "Ajout d'une image",
                    description = "Envoyez une image en pièce jointe pour l'ajouter au produit"
                )
            )