from cProfile import label
import os
from asyncio import Task, sleep
from socket import timeout
import time
import traceback
from typing import Literal
from discord import ButtonStyle, Embed, Interaction, Message, SelectOption, TextStyle
from classes.commands import Command
from classes.discord_wallet import PiWallet
from discord.ui import View, Modal, TextInput, Button, Select
from classes.emoji import Emoji
from classes.item import CommunityItem
from functions.utils import create_user_signin_channel, read_file, write_file
from init import COLOR, MODE, SELLER_ROLE_ID, log, client
from responses import default
from views.community_business import delete_view, discord_pre_payout, item_card_view, item_edit, main_edit_view, onchain_pre_payout, wallet_creation_view, wallet_payment_view
import asyncio

log.info("Community interaction bus registered")

async def interact(interaction: Interaction, id: str, values: list[str]):
    user_wallet = await PiWallet.from_user(interaction.user.id)
    components = id.split("#")
    match components[0]:
        case "BECOME_BUYER":
            if interaction.guild.get_role(SELLER_ROLE_ID) in interaction.user.roles:
                await interaction.response.send_message(
                    embed = Embed(
                        title = "Vous êtes déjà acheteur",
                        description = "Vous êtes déjà inscrit en tant qu'acheteur.",
                        color = COLOR
                    ),
                    ephemeral = True
                )
                return
            channel, message = await create_user_signin_channel(interaction.user, 'acheteur')
            if not message:
                embed, view = await wallet_creation_view(interaction, user_wallet, 'acheteur')
                message = await channel.send(
                    embed = embed,
                    view = view
                )
                data: dict[str, int] = await read_file("business/signin_channels.json")
                data[str(interaction.user.id)] = {
                    "channel_id": channel.id,
                    "message_id": message.id,
                }
                await write_file("business/signin_channels.json", data)
                await interaction.response.send_message(
                    embed = Embed(
                        title = "Votre salon d'inscription a été créé",
                        description = f"Rendez-vous sur votre salon privé {channel.mention} pour compléter les étapes de votre inscription en tant qu'acheteur.",
                        color = COLOR
                    ),
                    ephemeral = True
                )
        
            else:
                await interaction.response.send_message(
                    embed = Embed(
                        title = "Voici votre salon d'inscription",
                        description = f"Rendez-vous sur votre salon privé {channel.mention} pour compléter les étapes de votre inscription en tant qu'acheteur.",
                        color = COLOR
                    ),
                    ephemeral = True
                )
        
        case "BECOME_SELLER":
            if interaction.guild.get_role(SELLER_ROLE_ID) in interaction.user.roles:
                await interaction.response.send_message(
                    embed = Embed(
                        title = "Vous êtes déjà vendeur",
                        description = "Vous êtes déjà inscrit en tant que vendeur.",
                        color = COLOR
                    ),
                    ephemeral = True
                )
                return
            
            channel, message = await create_user_signin_channel(interaction.user, 'vendeur')
            if not message:
                embed, view = await wallet_creation_view(interaction, user_wallet, 'vendeur')
                message = await channel.send(
                    embed = embed,
                    view = view
                )
                data: dict[str, int] = await read_file("business/signin_channels.json")
                data[str(interaction.user.id)] = {
                    "channel_id": channel.id,
                    "message_id": message.id,
                }
                await write_file("business/signin_channels.json", data)
                await interaction.response.send_message(
                    embed = Embed(
                        title = "Votre salon d'inscription a été créé",
                        description = f"Rendez-vous sur votre salon privé {channel.mention} pour compléter les étapes de votre inscription en tant que vendeur.",
                        color = COLOR
                    ),
                    ephemeral = True
                )
        
            else:
                await interaction.response.send_message(
                    embed = Embed(
                        title = "Voici votre salon d'inscription",
                        description = f"Rendez-vous sur votre salon privé {channel.mention} pour compléter les étapes de votre inscription en tant que vendeur.",
                        color = COLOR
                    ),
                    ephemeral = True
                )
        
        case "CREATESILENTWALLET" | "UPDATE_PROFILE":
            wallet = await PiWallet.from_user(interaction.user.id)
            if not wallet:
                wallet = await PiWallet.create_new(interaction.user)

            try:
                wallet = await PiWallet.from_user(interaction.user.id)
                modal = Modal(
                    title = "Créer votre profil"
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
                        role: Literal['acheteur', 'vendeur'] = components[1]
                        wallet.locale = raw_locale.value.strip()
                        if wallet.address != raw_address.value.strip() or not wallet.is_verified:
                            await wallet.unverify()
                            wallet.address = raw_address.value.strip()

                        if role == "acheteur":
                            embed = await wallet.become_buyer()
                        
                        else:
                            embed = await wallet.become_seller()

                        await interaction2.response.edit_message(
                            embed = embed,
                            view = View()
                        )
                        

                    except:
                        log.warn(traceback.format_exc())

                modal.on_submit = on_profile_update
                await interaction.response.send_modal(modal)
            
            except:
                log.warn(traceback.format_exc())
        
        case "EDITITEM":
            product_id = int(components[-1])
            item = await CommunityItem.from_id(product_id)
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
                try:
                    item = await CommunityItem.from_id(product_id)
                    item.name = raw_name.value.strip()
                    item.price = int(raw_price.value.strip())
                    item.description = raw_description.value.strip()
                    await item.save()
                    if await item.message:
                        embed, view, file = await item_card_view(item)
                        await (await item.message).edit(
                            embed = embed,
                            view = view,
                            attachments = [file] if file else []
                        )
                    embed, view, file = await item_edit(interaction2, item)
                    await interaction2.response.edit_message(
                        embed = embed,
                        view = view,
                        attachments = [file] if file else []
                    )
                except:
                    log.warn(traceback.format_exc())
            
            modal.on_submit = on_product_update
            await interaction.response.send_modal(modal)
        
        case "ADDITEMIMAGE":
            product_id = int(components[-1])
            item = await CommunityItem.from_id(product_id)
            await interaction.response.edit_message(
                embed = Embed(
                    title = "Ajout d'une image",
                    description = "Envoyez une image en pièce jointe pour l'ajouter au produit.\nFormats acceptés: `png`, `jpg`, `jpeg`",
                ),
                view = View(timeout = None).add_item(
                    Button(
                        label = "Annuler",
                        custom_id = f"CANCELADDIMAGE#{item.id}",
                        emoji = Emoji.back.value
                    )
                ),
                attachments = []
            )

            def on_waited_interaction(interaction: Interaction):
                return interaction.data['custom_id'] == f"CANCELADDIMAGE#{item.id}"
            
            def on_waited_message(message: Message):
                if len(message.attachments) == 1:
                    if message.attachments[0].filename.endswith(".png") or message.attachments[0].filename.endswith(".jpg") or message.attachments[0].filename.endswith(".jpeg"):
                        return True
                    
            wait: tuple[
                set[Task[Interaction | Message]],  # done
                set[Task[Interaction | Message]]   # pending
            ] = await asyncio.wait(
                [
                    asyncio.create_task(client.wait_for("interaction", check = on_waited_interaction)),
                    asyncio.create_task(client.wait_for("message", check = on_waited_message))
                ],
                return_when = asyncio.FIRST_COMPLETED
            )
            done: set[Task[Interaction | Message]]
            pending: set[Task[Interaction | Message]]
            done, pending = wait
            for task in pending:
                task.cancel()

            for task in done:
                result = task.result()
                if isinstance(result, Interaction):
                    interaction2 = result
                    log.debug('Annulation')
                    embed, view, file = await item_edit(interaction, item, len(interaction.message.components) == 5)
                    await interaction2.response.edit_message(
                        embed = embed,
                        view = view,
                        attachments = [file] if file else []
                    )
                
                else:
                    message = result
                    await message.attachments[0].save(f"data/business/images/{item.id}.png")
                    if await item.message:
                        embed, view, file = await item_card_view(item)
                        await (await item.message).edit(
                            embed = embed,
                            view = view,
                            attachments = [file] if file else []
                        )
                    embed, view, file = await item_edit(interaction, item, len(interaction.message.components) == 5)
                    await interaction.edit_original_response(
                        embed = embed,
                        view = view,
                        attachments = [file] if file else []
                    )
            
        case "PUBLISHITEM":
            item_id = int(components[-1])
            item = await CommunityItem.from_id(item_id)
            if not await item.message:
                if MODE == "DEV":
                    channel = client.get_channel(1310526655101407232)
                
                embed, view, file = await item_card_view(item)
                msg = await channel.send(
                    embed = embed,
                    view = view,
                    file = file
                )
                item.message_id = msg.id
                item.channel_id = channel.id
                await item.save()
                await interaction.response.edit_message(
                    embed = Embed(
                        title = "Votre produit a été publié !",
                        description = f"{client.user.display_name} vous enverra un MP lorsque quelqu'un achètera votre produit",
                        color = COLOR
                    ),
                    attachments = []
                )

        case "SELECTITEM":
            item_id = int(values[0])
            item = await CommunityItem.from_id(item_id)
            embed, view, file = await item_edit(interaction, item, True)
            await interaction.response.edit_message(
                embed = embed,
                view = view,
                attachments = [file] if file else []
            )
        
        case "BACKITEM":
            embed, view = await main_edit_view(interaction.user)
            await interaction.response.edit_message(
                embed = embed,
                view = view,
                attachments = []
            )
        
        case "SETPAYMENTMETHOD":
            item_id = int(components[-1])
            item = await CommunityItem.from_id(item_id)
            method: Literal['onchain', 'discord', 'any'] = values[0]
            item.payment_method = method
            await item.save()
            if await item.message:
                embed, view, file = await item_card_view(item)
                await (await item.message).edit(
                    embed = embed,
                    view = view,
                    attachments = [file] if file else []
                )
            embed, view, file = await item_edit(interaction, item, len(interaction.message.components) == 5)
            await interaction.response.edit_message(
                embed = embed,
                view = view,
                attachments = [file] if file else []
            )
            
        case "SETFEES":
            item_id = int(components[-1])
            item = await CommunityItem.from_id(item_id)
            fees: Literal["included", "euro", "none"] = values[0]
            item.fees = fees
            await item.save()
            if await item.message:
                embed, view, file = await item_card_view(item)
                await (await item.message).edit(
                    embed = embed,
                    view = view,
                    attachments = [file] if file else []
                )
            embed, view, file = await item_edit(interaction, item, len(interaction.message.components) == 5)
            await interaction.response.edit_message(
                embed = embed,
                view = view,
                attachments = [file] if file else []
            )
        
        case "DELETEITEM":
            item_id = int(components[-1])
            item = await CommunityItem.from_id(item_id)
            embed, view = await delete_view(item)
            await interaction.response.edit_message(
                embed = embed,
                view = view,
                attachments = []
            )
        
        case "CONFIRMDELETEITEM":
            item_id = int(components[-1])
            item = await CommunityItem.from_id(item_id)
            await (await item.message).delete()
            os.remove(f"data/business/sales/{item_id}.json")
            try:
                os.remove(f'data/business/images/{item_id}.png')
            
            except:
                pass
            
            embed, view = await main_edit_view(interaction.user)
            await interaction.response.edit_message(
                embed = embed,
                view = view,
                attachments = []
            )
        
        case "DESTROY":
            await interaction.response.edit_message()
            await interaction.delete_original_response()

        case "BUYITEM":
            item_id = int(components[-1])
            item = await CommunityItem.from_id(item_id)
            if item:
                if item.payment_method == "any":
                    await interaction.response.send_message(
                        embed = Embed(
                            title = "Choisir une méthode de paiement",
                            description = "Vous pous pouvez payer via votre wallet Discord ou votre wallet Mainnet pour acheter cet article.\nQuelle méthode souhaitez vous utiliser pour cet achat ?",
                            color = COLOR
                        ),
                        view = View(timeout = None).add_item(
                            Select(
                                placeholder = "Méthode de paiement",
                                custom_id = f"PAYWITH#{item.id}",
                                options = [
                                    SelectOption(
                                        label = "Wallet Discord",
                                        value = "discord",
                                        description = "Utilisez le solde de votre wallet Discord pour payer instantanément"
                                    ),
                                    SelectOption(
                                        label = "OnChain",
                                        value = "onchain",
                                        description = "Utilisez la blockchain pour votre paiement"
                                    )
                                ]
                            )
                        ),
                        ephemeral = True
                    )
                
                elif item.payment_method == "discord":
                    embed, view = discord_pre_payout(item)
                    await interaction.response.send_message(
                        embed = embed,
                        view = view,
                        ephemeral = True
                    )
                
                elif item.payment_method == "onchain":
                    embed, view = onchain_pre_payout(item)
                    await interaction.response.send_message(
                        embed = embed,
                        view = view,
                        ephemeral = True
                    )
            
            else:
                await interaction.response.send_message(
                    embed = Embed(
                        title = "Achat impossible",
                        description = "Cet article n'existe plus.",
                        color = COLOR
                    ),
                    ephemeral = True
                )
        
        case "PAYWITH":
            item_id = int(components[-1])
            item = await CommunityItem.from_id(item_id)
            method: Literal["discord", "onchain"] = values[0]
            if method == "discord":
                embed, view = discord_pre_payout(item)
                
            elif method == "onchain":
                embed, view = onchain_pre_payout(item)

            await interaction.response.edit_message(
                embed = embed,
                view = view
            )
        
        case "CONFIRMBUY":
            item_id = int(components[-1])
            item = await CommunityItem.from_id(item_id)
            selected_method: Literal["discord", "onchain"] = components[1]
            if selected_method == "discord":
                wallet = await PiWallet.from_user(interaction.user.id)
                if not wallet:
                    await interaction.response.edit_message(
                        embed = Embed(
                            title = "Wallet introuvable",
                            description = "Vous devez disposer d'un wallet Discord pour acheter cet article.",
                            color = COLOR
                        ),
                        ephemeral = True
                    )
                
                else:
                    try:
                        await wallet.send(item.price, await PiWallet.from_user(item.seller_id))
                        try:
                            item_card = await item.message
                            button = item_card.components[0].children[0]
                            new_bt = Button()
                            new_bt.label = button.label
                            new_bt.emoji = button.emoji
                            new_bt.custom_id = button.custom_id
                            if item.sell_type == "unique":
                                new_bt.style = ButtonStyle.gray
                                new_bt.disabled = True
                            
                            else:
                                new_bt.style = ButtonStyle.green
                            
                            await (await item.message).edit(
                                view = View(timeout = None).add_item(new_bt)
                            )
                        
                        except:
                            log.warn(traceback.format_exc())
                            pass
                        
                        try:
                            await item.seller.send(
                                embed = Embed(
                                    title = "Objet vendu !",
                                    description = f"Vous avez vendu {item.name} pour {item.price} π à {interaction.user.display_name}. Contactez-le par MP pour livrer le produit.",
                                    color = COLOR
                                )
                            )
                        
                        except:
                            log.warn(traceback.format_exc())
                        
                        msg = await interaction.user.send(
                            embed = Embed(
                                title = "Confirmation d'achat",
                                description = f"Vous avez acheté {item.name} pour {item.price} π auprès de {item.seller.display_name}. Vous pouvez vous rapprocher de {item.seller.display_name} via MP pour discuter des modalités d'envoi.\nID de transaction: {interaction.id}.",
                                color = COLOR
                            )
                        )
                        await interaction.response.edit_message(
                            embed = Embed(
                                title = "Achat confirmé",
                                description = f"Félicitations, vous venez d'acheter {item.name} ! Retrouvez votre [confirmation d'achat]({msg.jump_url}) dans vos MP.",
                                color = COLOR
                            ),
                            view = View()
                        )
                    
                    except PiWallet.FundsError:
                        log.debug('Nope pas de sous')
                        await interaction.response.edit_message(
                            embed = Embed(
                                title = "Fonds insuffisants",
                                description = "Votre solde discord ne permet pas cet achat. Veuillez approvisionner votre solde ou changer de méthode de paiement si disponible.",
                                color = COLOR
                            )
                        )
                    
                    except:
                        log.warn(traceback.format_exc())

            else:
                await item.seller.send(
                    embed = Embed(
                        title = "Réservation d'objet",
                        description = f"{interaction.user.display_name} est sur le point d'acheter {item.name} via OnChain. {client.user.display_name} vous enverra un message dès qu'il détecte le paiement sur la blockchain. Si BitBot ne la détecte pas, vérifiez votre historique de paiement.",
                        color = COLOR,
                    )
                )
                await interaction.response.edit_message(
                    embed = Embed(
                        title = "Effectuer la transaction sur le Pi Browser",
                        description = f"{client.user.display_name} a averti {item.seller.display_name} de votre réservation.\nEnvoyez **EXACTEMENT** {item.price} π à cette adresse :\n ```{(await PiWallet.from_user(item.seller_id)).address}```. {client.user.display_name} vérifiera la transaction sur la blockchain et avertira {item.seller.display_name} dès que vous aurez effectué la transaction.",
                        color = COLOR
                    )
                )
            
        case "SELECTITEMSELLTYPE":
            item_id = int(id.split("#")[1])
            item = await CommunityItem.from_id(item_id)
            sell_type: Literal["unique", "multi"] = values[0]
            item.sell_type = sell_type
            await item.save()
            embed, view, file = await item_edit(interaction, item, len(interaction.message.components) == 5)
            await interaction.response.edit_message(
                embed = embed,
                view = view,
                attachments = [file] if file else []
            )
        
        case "PAUSEITEM":
            item_id = int(id.split("#")[1])
            item = await CommunityItem.from_id(item_id)
            message = await item.message
            if message:
                item.is_paused = True
                await item.save()
                embed, view, file = await item_edit(interaction, item, len(interaction.message.components) == 5)
                await interaction.response.edit_message(
                    embed = embed,
                    view = view,
                    attachments = [file] if file else []
                )
                button = message.components[0].children[0]
                new_button = Button()
                new_button.label = button.label
                new_button.emoji = button.emoji
                new_button.custom_id = button.custom_id
                new_button.disabled = True
                new_button.style = ButtonStyle.gray
                await message.edit(view = View(timeout = None).add_item(new_button))
            
            else:
                await interaction.response.send_message(
                    embed = Embed(
                        title = "Votre produit n'est plus en ligne",
                        description = "Vous ne pouvez pas suspendre une annonce qui n'a pas encore été publiée.",
                        color = COLOR
                    ),
                    ephemeral = True
                )
        
        case "PLAYITEM":
            item_id = int(id.split("#")[1])
            item = await CommunityItem.from_id(item_id)
            message = await item.message
            if message:
                item.is_paused = False
                await item.save()
                button = message.components[0].children[0]
                new_button = Button()
                new_button.label = button.label
                new_button.emoji = button.emoji
                new_button.custom_id = button.custom_id
                new_button.disabled = False
                new_button.style = ButtonStyle.green
                await message.edit(view = View(timeout = None).add_item(new_button))
                embed, view, file = await item_edit(interaction, item, len(interaction.message.components) == 5)
                await interaction.response.edit_message(
                    embed = embed,
                    view = view,
                    attachments = [file] if file else []
                )
            
            else:
                await interaction.response.send_message(
                    embed = Embed(
                        title = "Votre produit n'est plus en ligne",
                        description = "Vous ne pouvez pas relancer une annonce qui n'est plus en ligne. Publiez là à nouveau pour reprendre les ventes",
                        color = COLOR
                    ),
                    ephemeral = True
                )
        
        case "BACKITEMID":
            item_id = int(id.split("#")[1])
            item = await CommunityItem.from_id(item_id)
            embed, view, file = await item_edit(interaction, item, len(interaction.message.components) == 5)
            await interaction.response.edit_message(
                embed = embed,
                view = view,
                attachments = [file] if file else []
            )