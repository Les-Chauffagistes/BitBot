from discord import ChannelType, Embed, Interaction

from classes.brand import Brand
from classes.commands import Command
from classes.discord_wallet import PiWallet
from commands import commands
from init import ADMIN_NOTIFICATIONS_CHANNEL_ID, COLOR, client, log
from views.user_business import card_view, main_brand_view, main_shop_view, payment_confirm

async def interact(interaction: Interaction, id: str, values: list[str]):
    assert client.user
    match id.split("#")[0]:
        case "OPENSHOP":
            try:
                embed, view = await main_shop_view()
                msg = await interaction.user.send(
                    embed = embed,
                    view = view
                )
                await interaction.response.send_message(
                    embed = Embed(
                        title = "Vous pouvez continuer en MP",
                        description = f"La boutique Fulcran s'est ouverte dans vos MP: {msg.jump_url}",
                        color = COLOR
                    ),
                    ephemeral = True
                )
            
            except:
                await interaction.response.send_message(
                    embed = Embed(
                        title = "Impossible de poursuivre en MP",
                        description = f"Vous n'autorisez pas {client.user.display_name} à vous anvoyer des messages privés. Modifiez vos paramètres de confidentialité sur le serveur et autorisez les autres membres à vous envoyer de messages privés.\n\nVous ne pourrez pas acheter d'objets dans la boutique Fulcran si vous ne modifiez pas ces paramètres. BitBot vous envoie votre facture et votre code d'acitvation en MP.",
                        color = COLOR
                    ),
                    ephemeral = True
                )

        case "USERSELECTBRAND":
            brand_id = int(values[0])
            brand = await Brand.from_id(brand_id)
            embed, view = main_brand_view(brand)
            await interaction.response.edit_message(
                embed = embed,
                view = view
            )

        case "USERBACKTOBRAND":
            embed, view = await main_shop_view()
            await interaction.response.edit_message(
                embed = embed,
                view = view,
            )
        
        case "USERSELECTCARD":
            brand_id = int(id.split("#")[1])
            brand = await Brand.from_id(brand_id)
            card_id = int(values[0])
            card = brand.get_card(card_id)
            if card:
                embed, view = card_view(brand, card)
                await interaction.response.edit_message(
                    embed = embed,
                    view = view
                )
        
        case "BACKTOBRANDID":
            brand_id = int(id.split("#")[1])
            brand = await Brand.from_id(brand_id)
            embed, view = main_brand_view(brand)
            await interaction.response.edit_message(
                embed = embed,
                view = view,
            )
        
        case "BUYCARD":
            brand_id = int(id.split("#")[1])
            brand = await Brand.from_id(brand_id)
            card_id = int(id.split("#")[2])
            card = brand.get_card(card_id)
            wallet = await PiWallet.from_user(interaction.user.id)
            if card:
                if wallet:
                    if wallet.balance >= card.price:
                        embed, view = payment_confirm(brand, card)
                        await interaction.response.edit_message(
                            embed = embed,
                            view = view
                        )
                    
                    else:
                        await interaction.response.send_message(
                            embed = Embed(
                                title = "Solde insuffisant",
                                description = f"Votre solde ne permet pas un tel achat. Vous avez {int(wallet.balance)} π sur votre wallet Discord. Déposez davantage de fonds avec la commande {Command.pi_deposit}, puis réessayez.",
                                color = COLOR
                            ),
                            ephemeral = True
                        )
                
                else:
                    await interaction.response.send_message(
                        embed = Embed(
                            title = "Vous n'avez pas de wallet Pi sur Discord",
                            description = f"Le moyen de paiement sur la boutique Fulcran est le wallet Pi Discord. Pour acheter depuis la boutique, créez un wallet et déposez des fonds avec la commande {Command.pi_deposit}",
                            color = COLOR
                        ),
                        ephemeral = True
                    )
        
        case "BACKTOCARD":
            brand_id = int(id.split("#")[1])
            brand = await Brand.from_id(brand_id)
            card_id = int(id.split("#")[2])
            card = brand.get_card(card_id)
            if card:
                embed, view = card_view(brand, card)
                await interaction.response.edit_message(
                    embed = embed,
                    view = view
                )
        
        case "CONFIRMCARDPAYMENT":
            brand_id = int(id.split("#")[1])
            brand = await Brand.from_id(brand_id)
            card_id = int(id.split("#")[2])
            card = brand.get_card(card_id)
            if card:
                if card.codes:
                    wallet = await PiWallet.from_user(interaction.user.id)
                    if wallet:
                        try:
                            await wallet.remove_pi(card.current_price)
                            fulcran = await PiWallet.from_user(276123659050024962)
                            assert fulcran, "Yo comment ça mon reuf refais ton wallet"
                            await fulcran.add_pi(card.current_price)
                            code = await card.drop_code()
                            await interaction.response.edit_message(
                                embed = Embed(
                                    title = f"Votre code d'activation {brand.name}",
                                    description = f"Merci pour votre achat !\nVous avez acheté **{card.name}** pour **{card.current_price} π**.\n\n Voici votre code d'activation:\n||```{code}```||\nN° de commande: {interaction.id}",
                                    color = COLOR
                                ),
                                view = None
                            )
                            await client.get_channel(ADMIN_NOTIFICATIONS_CHANNEL_ID).send(
                                embed = Embed(
                                    title = "Achat automatique effectué",
                                    description = f"{interaction.user.display_name} a acheté **{card.name}** de l'enseigne {brand.name} pour **{card.current_price} π**.\n\nCode d'activation fourni: `{code}`\nN° de commande: {interaction.id}",
                                    color = COLOR
                                ).set_author(
                                    name = interaction.user.display_name,
                                    icon_url = interaction.user.display_avatar.url
                                )
                            )
                        
                        except PiWallet.FundsError:
                            await interaction.response.send_message(
                                embed = Embed(
                                    title = "Solde insuffisant",
                                    description = "Le montant de votre commande est trop important. Veuillez déposer davantage de fonds sur votre wallet Discord.",
                                    color = COLOR
                                ),
                                ephemeral = True
                            )
                    
                    else:
                        await interaction.response.send_message(
                            embed = Embed(
                                title = "Achat impossible",
                                description = f"Vous devez posséder un wallet Pi Discord pour acheter un produit sur la boutique Fulcran. Créez-en un avec la commande {Command.pi_deposit}.",
                                color = COLOR    
                            ),
                            ephemeral = True
                        )
                
                else:
                    await interaction.response.send_message(
                        embed = Embed(
                            title = "Achat impossible",
                            description = "Le produit est en rupture de stock. Restez à l'affut !",
                            color = COLOR
                        ),
                        ephemeral = True
                    )
