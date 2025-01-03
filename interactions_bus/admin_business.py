import traceback
from discord import ButtonStyle, Embed, Interaction
from discord.utils import MISSING
from requests import delete
from classes.discord_wallet import PiWallet
from classes.emoji import Emoji
from classes.item import AdminItem
from modules.pinet.classes import Wallet
from views.admin_business import confirm_payment_view, item_modal, item_variante_modal, item_variante_view, item_view, preview_item_variant, product_view, select_channel, select_variante_purchase_view
from init import ADMIN_NOTIFICATIONS_CHANNEL_ID, COLOR, FULCRAN_ID, GUILD_ID, SERVER_NAME, log, client
from discord.ui import View, Button, Modal, TextInput



async def interact(interaction: Interaction, id: str, values: list[str]):
    match id.split("#")[0]:
        case "BUSINESSEDITITEM":
            item_id = int(id.split("#")[1])
            item = await AdminItem.from_id(item_id)
            modal, raw_name, raw_description = item_modal(item)
            async def on_item(interaction2: Interaction):
                try:
                    item.name = raw_name.value.strip()
                    item.description = raw_description.value.strip()
                    await item.save()
                    embed, view, file = await item_view(item) 
                    await interaction2.response.edit_message(
                        embed = embed,
                        view = view,
                        attachments = [file] if file else []
                    )
                
                except:
                    log.warn(traceback.format_exc())

            modal.on_submit = on_item
            await interaction.response.send_modal(modal)
            
        case "BUSINESSEDITITEMVARIANTE":
            item_id = int(id.split("#")[1])
            variante_id = int(id.split("#")[2])
            item = await AdminItem.from_id(item_id)
            modal, raw_name, raw_description, raw_price, raw_promo = item_variante_modal(item, item.get_variante(variante_id))
            
            async def on_variante(interaction2: Interaction):
                try:
                    variante = item.get_variante(variante_id)
                    variante.name = raw_name.value.strip()
                    variante.description = raw_description.value.strip()
                    variante.price = int(raw_price.value.strip())
                    variante.promo = raw_promo.value.strip()
                    await variante.item.save()
                    embed, view, file = item_variante_view(item, variante)
                    await interaction2.response.edit_message(
                        embed = embed,
                        view = view,
                        attachments = [file] if file else []
                    )
                except:
                    log.warn(traceback.format_exc())
                
            modal.on_submit = on_variante
            await interaction.response.send_modal(modal)
        
        case "BUSINESSSELECTVARIANTEID":
            item_id = int(id.split("#")[1])
            item = await AdminItem.from_id(item_id)
            variante_id = values[0]
            if variante_id == "NEW":
                modal, raw_name, raw_description, raw_price, raw_promo = item_variante_modal(item, None)
                async def on_variante(interaction2: Interaction):
                    try:
                        variante = await item.create_variante(interaction.id, raw_name.value.strip(), raw_description.value.strip(), int(raw_price.value.strip()), raw_promo.value.strip())
                        embed, view, file = item_variante_view(item, variante)
                        await interaction2.response.edit_message(
                            embed = embed,
                            view = view,
                            attachments = [file] if file else []
                        )

                    except:
                        log.warn(traceback.format_exc())
                
                modal.on_submit = on_variante
                await interaction.response.send_modal(modal)

            else: 
                embed, view, file = item_variante_view(item, item.get_variante(variante_id))
                await interaction.response.edit_message(
                    embed = embed,
                    view = view,
                    attachments = [file] if file else []
                )
        
        case "BUSINESSDELETEITEMVARIANTE":
            item_id = int(id.split("#")[1])
            variante_id = int(id.split("#")[2])
            item = await AdminItem.from_id(item_id)
            variante = item.get_variante(variante_id)
            await interaction.response.send_message(
                embed = Embed(
                    title = f"Supprimer une variante de {item.name} ?",
                    description = f"Cette action est irreversible. Supprimer la variante « {variante.name} » ?",
                    color = COLOR
                ),
                view = View(timeout = None).add_item(
                    Button(
                        label = "Annuler",
                        custom_id = "DESTROY",
                    )
                ).add_item(
                    Button(
                        label = "Supprimer",
                        style = ButtonStyle.danger,
                        custom_id = "BUSINESSCONFIRMDELETEITEMVARIANTE#" + str(item_id) + "#" + str(variante_id),
                        emoji = Emoji.delete.value
                    )
                )
            )
        
        case "BUSINESSCONFIRMDELETEITEMVARIANTE":
            item_id = int(id.split("#")[1])
            variante_id = int(id.split("#")[2])
            item = await AdminItem.from_id(item_id)
            await item.delete_variante(variante_id)
            embed, view, file = await item_view(item)
            await interaction.response.edit_message(
                embed = embed,
                view = view,
                attachments = [file] if file else []
            )

        case "BUSINESSSELECTIEM":
            item_id = int(id.split("#")[1])
            item = await AdminItem.from_id(item_id)
            embed, view, file = await item_view(item)
            await interaction.response.edit_message(
                embed = embed,
                view = view,
                attachments = [file] if file else []
            )
        
        case "BUSINESSPUBLISHITEM":
            item_id = int(id.split("#")[1])
            item = await AdminItem.from_id(item_id)
            embed, view = select_channel(item)
            await interaction.response.edit_message(
                embed = embed,
                view = view,
            )
        
        case "BUSINESSSELECTCHANNEL":
            item_id = int(id.split("#")[1])
            item = await AdminItem.from_id(item_id)
            channel_id = int(values[0])
            item.channel_id = channel_id
            embed, view, file = await product_view(item)
            message = await client.get_channel(channel_id).send(
                embed = embed,
                view = view,
                file = file if file else MISSING
            )
            item.message_id = message.id
            await item.save()
            await interaction.response.send_message(
                embed = Embed(
                    title = "Produit publié",
                    description = f"Votre produit a été publié dans le salon {item.channel.mention}.",
                    color = COLOR
                )
            )
            embed, view, file = await item_view(item)
            await interaction.message.edit(
                embed = embed,
                view = view,
                attachments = [file] if file else []
            )
        
        case "BUYBUSINESSSHOPITEM":
            item_id = int(id.split("#")[1])
            item = await AdminItem.from_id(item_id)
            embed, view = select_variante_purchase_view(item)
            await interaction.response.send_message(
                embed = embed,
                view = view,
                ephemeral = True
            )

        case "BUSINESSSELECTPURCHASEITEM":
            item_id = int(id.split("#")[1])
            item = await AdminItem.from_id(item_id)
            variante_id = int(values[0])
            variante = item.get_variante(variante_id)
            embed, view = preview_item_variant(item, variante)
            await interaction.response.edit_message(
                embed = embed,
                view = view
            )
        
        case "BUSINESSPURCHASEITEM":
            item_id = int(id.split("#")[1])
            item = await AdminItem.from_id(item_id)
            variante_id = int(id.split("#")[2])
            variante = item.get_variante(variante_id)
            embed, view = confirm_payment_view(item, variante)
            await interaction.response.edit_message(
                embed = embed,
                view = view
            )
        
        case "BUSINESSCONFIRMPAYMENT":
            item_id = int(id.split("#")[1])
            item = await AdminItem.from_id(item_id)
            variante_id = int(id.split("#")[2])
            variante = item.get_variante(variante_id)
            wallet = await PiWallet.from_user(interaction.user.id)
            if wallet:
                if wallet.is_verified:
                    if wallet.balance >= variante.user_price:
                        await wallet.remove_pi(variante.user_price)
                        
                        try:
                            message = await interaction.user.send(
                                embed = Embed(
                                    title = "Reçu pour l'achat sur le serveur",
                                    description = f"Vous avez acheté {item.name} : {variante.name} pour **{variante.user_price} π** sur la boutique Fulcran. Si le produit est dématérialisé, vous allez recevoir le code d'activation dans vos MP dans quelques instants.\n\nN° de commande: {interaction.id}",
                                    color = COLOR
                                )
                            )
                        
                        except:
                            message = None

                        await interaction.response.edit_message(
                            embed = Embed(
                                title = "Confirmation d'achat",
                                description = f"Félicitations ! Vous avez acheté {item.name} : {variante.name} pour **{variante.user_price} π**. {f" Retrouvez votre [confirmation d'achat]({message.jump_url}) dans vos MP" if message else f"\n\n## ⚠️ {client.user.display_name} ne peut pas pu vous envoyer de MP\nVotre confirmation d'achat n'a pas pu être envoyée. Autorisez {client.user.display_name} à vous envoyer des MP depuis les réglages de confidentialité du serveur {SERVER_NAME}, ou vous ne pourrez pas recevoir votre produit.\n\nN° de commande: {interaction.id}"}.",
                            ),
                            view = View()
                        )

                        f_wallet = await PiWallet.from_user(FULCRAN_ID)
                        await f_wallet.add_pi(variante.user_price)
                        await client.get_channel(ADMIN_NOTIFICATIONS_CHANNEL_ID).send(
                            embed = Embed(
                                title = "Nouvelle commande",
                                description = f"Nouvelle commande passée dans la boutique **Fulcran**\n\n## {item.name} : {variante.name}",
                                color = COLOR
                            ).set_author(
                                name = interaction.user.display_name,
                                icon_url = interaction.user.display_avatar.url
                            ),
                            view = View(timeout = None).add_item(
                                Button(
                                    label = "Envoyer le code",
                                    emoji = Emoji.send.value,
                                    custom_id = f"SENDCODE#{interaction.user.id}#{item.id}#{variante.id}",
                                )
                            )
                        )
                        return
                    
                    else:
                        await interaction.response.edit_message(
                            embed = Embed(
                                title = "Fonds insuffisants",
                                description = "Vous n'avez pas assez de Pi pour acheter ce produit. Effectuez un dépot, puis réessayez.",
                                color = COLOR
                            ),
                            view = View()
                        )
                        return
            
                await interaction.response.send_message(
                    embed = Embed(
                        title = "Rejoindre les acheteurs",
                        description = f"Vous n'êtes pas inscrit en tant qu'acheteur sur {SERVER_NAME}. Abonnez-vous pour acheter des produits sans frais sur le serveur.",
                        color = COLOR
                    )
                )
        
        case "SENDCODE":
            user_id = int(id.split("#")[1])
            item_id = int(id.split("#")[2])
            variante_id = int(id.split("#")[3])
            modal = Modal(title = "Envoyer un code d'activation")
            raw_code = TextInput(
                label = f"Code d'activation",
            )
            modal.add_item(raw_code)
            async def on_code(interaction2: Interaction):
                try:
                    item = await AdminItem.from_id(item_id)
                    variante = item.get_variante(variante_id)
                    await client.get_user(user_id).send(
                        embed = Embed(
                            title = f"Votre code d'activation de {item.name} : {variante.name}",
                            description = f"||```{raw_code.value.strip()}```||",
                            color = COLOR
                        )
                    )
                    await interaction2.response.send_message(
                        embed = Embed(
                            title = "Code envoyé",
                            description = f"{client.get_user(user_id).display_name} a bien reçu le code",
                            color = COLOR
                        ),
                        ephemeral = True
                    )
                    await interaction.message.edit(
                        view = View()
                    )

                except:
                    await interaction2.response.send_message(
                        embed = Embed(
                            title = "Impossible d'envoyer le code",
                            description = "L'utilisateur est introuvable ou n'autorise pas les messages du bot.",
                            color = COLOR
                        ),
                        ephemeral = True
                    )

            modal.on_submit = on_code
            await interaction.response.send_modal(modal)