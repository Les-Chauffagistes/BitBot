import os
import traceback
from typing import Literal, Optional
from discord import ButtonStyle, Embed, File, Interaction, SelectOption, User
from classes.commands import Command
from classes.discord_wallet import PiWallet
from classes.emoji import Emoji
from classes.item import CommunityItem
from functions.utils import read_file
from init import BUYER_ROLE_ID, COLOR, GUILD_ID, SELLER_ROLE_ID, log, client
from discord.ui import View, Button, Select


async def wallet_creation_view(interaction: Interaction, user_wallet: Optional[PiWallet], role: Literal['vendeur', 'acheteur']):
    if not user_wallet:
        embed = Embed(
            title = f"Devenir {role}",
            description = f"Pour devenir {role}, vous devez disposer d'un wallet Discord, même si vous ne comptez pas l'utiliser. Il permet de vérifier votre adresse Pi Network. Vous ne disposez pas de wallet. Créez-en un en cliquant sur le bouton ci-dessous.",
            color = COLOR
        )
        view = View(timeout = None).add_item(
            Button(
                label = "Créer un wallet",
                emoji = Emoji.wallet.value,
                custom_id = f"CREATESILENTWALLET#{role}#{interaction.user.id}"
            )
        )
        return embed, view
    
    else:
        embed = Embed(
            title = f"Devenir {role}",
            description = f"Pour devenir {role}, vous devez disposer d'un wallet Discord, même si vous ne comptez pas l'utiliser. Il permet de vérifier votre adresse Pi Network. Vous disposez déjà d'un wallet Discord, vous pouvez passer à la prochaine étape !",
            color = COLOR
        )
        view = View(timeout = None).add_item(
            Button(
                label = "Suivant",
                emoji = Emoji.next.value,
                custom_id = f"UPDATE_PROFILE#{role}#{interaction.user.id}"
            )
        )
        return embed, view

async def wallet_verification_view(interaction: Interaction, user_wallet: Optional[PiWallet], role: Literal['vendeur', 'acheteur']):
    if not user_wallet.is_verified:
        embed = Embed(
            title = f"Devenir {role}",
            description = f"Pour devenir {role}, vous devez avoir un profil Pi verifié. Completez votre profil et effectuez l'étape de vérification pour passer à la dernière étape",
            color = COLOR
        )
        view = View(timeout=None).add_item(
            Button(
                label = "Mettre à jour mon profil",
                emoji = Emoji.profile.value,
                custom_id = f"UPDATE_PROFILE#{role}#{interaction.user.id}"
            )
        )
        return embed, view

async def wallet_payment_view(interaction: Interaction, user_wallet: Optional[PiWallet], role: Literal['vendeur', 'acheteur']):
    role_buyer = interaction.guild.get_role(BUYER_ROLE_ID)
    role_seller = interaction.guild.get_role(SELLER_ROLE_ID)
    
    if role == 'acheteur':
        discord_role = role_buyer
    
    else:
        discord_role = role_seller

    if not discord_role in interaction.user.roles:
        embed = Embed(
            title = f"Devenir {role}",
            description = f"L'inscription en tant que {role} est payante. Déposez au moins {'2' if role == 'acheteur' else '5'} Pi sur votre Wallet Discord, et payez votre inscription pour finaliser votre inscription.",
            color = COLOR
        )
        view = View(timeout=None).add_item(
            Button(
                label = "Payer l'inscription",
                emoji = Emoji.pay.value,
                custom_id = f"PAY_INSCRIPTION#{role}#{interaction.user.id}"
            )
        )
        return embed, view
    
    else:
        await interaction.response.send_message(
            embed = Embed(
                title = "Inscription déjà validée",
                description = f"Vous avez déjà obtenu les privilèges {role}",
                color = COLOR
            ),
            ephemeral = True
        )

async def item_edit(interaction: Interaction, item: CommunityItem = None, with_back: bool = False):
    embed = Embed(
        title = "Gérer le produit",
        description = f"# {item.name}\n{item.description}\n### **{item.price}** Pi",
        color = COLOR
    ).set_image(
        url = "attachment://image.png"
    )
    view = View(timeout = None).add_item(
        Button(
            label= "Modifier",
            emoji = Emoji.edit.value,
            style = ButtonStyle.primary,
            custom_id = f"EDITITEM#{item.id}"
        )
    ).add_item(
        Button(
            label = "Définir l'image",
            emoji = Emoji.image.value,
            style = ButtonStyle.primary,
            custom_id = f"ADDITEMIMAGE#{item.id}"
        )
    )
    if await item.message:
        if not item.is_paused:
            view.add_item(
                Button(
                    label = "Suspendre",
                    emoji = Emoji.pause.value,
                    custom_id = f"PAUSEITEM#{item.id}"
                )
            )
        
        else:
            view.add_item(
                Button(
                    label = "Reprendre",
                    emoji = Emoji.play.value,
                    custom_id = f"PLAYITEM#{item.id}"
                )
            )
        view.add_item(
            Button(
                label = "Supprimer",
                emoji = Emoji.delete.value,
                style = ButtonStyle.danger,
                custom_id = f"DELETEITEM#{item.id}"
            )
        )
    
    else:
        view.add_item(
            Button(
                label = "Publier",
                emoji = Emoji.share.value,
                style = ButtonStyle.green,
                custom_id = f"PUBLISHITEM#{item.id}"
            ) 
        )
    
    view.add_item(
        Select(
            placeholder = "Méthode de paiement",
            custom_id = f"SETPAYMENTMETHOD#{item.id}",
            options = [
                SelectOption(
                    label = "Paiement OnChain",
                    description = "Via mainnet",
                    value = "onchain",
                    default = item.payment_method == "onchain"
                ),
                SelectOption(
                    label = "Paiement Discord",
                    description = "Via Discord",
                    value = "discord",
                    default = item.payment_method == "discord"
                ),
                SelectOption(
                    label = "Peu importe",
                    description = "Laissez l'acheteur choisir",
                    value = "any",
                    default = item.payment_method == "any"
                )
            ]
        )
    ).add_item(
        Select(
            placeholder = "Frais de ports",
            custom_id = f"SETFEES#{item.id}",
            options = [
                SelectOption(
                    label = "Frais inclus dans le prix",
                    description = "Le prix comprend les frais de ports",
                    value = "included",
                    default = item.fees == "included"
                ),
                SelectOption(
                    label = "Frais non inclus",
                    description = "L'acheteur paie les frais de ports en Euro",
                    value = "euro",
                    default = item.fees == "euro"
                ),
                SelectOption(
                    label = "Non applicable",
                    description = "Le produit est dématérialisé",
                    value = "none",
                    default = item.fees == "none"
                )
            ]
        )
    ).add_item(
        Select(
            placeholder = "Type de vente",
            options = [
                SelectOption(
                    label = "Vente unique",
                    description = "Votre publication sera retirée lorsqu'un utilisateur achetera votre article",
                    value = 'unique',
                    default = item.sell_type == "unique"
                ),
                SelectOption(
                    label = "Vente multiple",
                    description = "Vendez cet article plusieurs fois. Votre produit restera visible après un achat",
                    value = 'multi',
                    default = item.sell_type == "multi"
                )
            ],
            custom_id = f"SELECTITEMSELLTYPE#{item.id}"
        )
    )
    if with_back:
        view.add_item(
            Button(
                label = "Retour",
                emoji = Emoji.back.value,
                custom_id = "BACKITEM",
                row = 4
            )
        )

    return embed, view, File(f"data/business/images/{item.id}.png", "image.png") if os.path.exists(f"data/business/images/{item.id}.png") else None

async def main_edit_view(user: User):
    sales: list[CommunityItem] = []
    for file_name in os.listdir("data/business/sales"):
        try:
            file_data = await read_file(f"business/sales/{file_name}")
            if file_data['seller_id'] == user.id:
                sales.append(await CommunityItem.from_id(file_data["id"]))
        
        except:
            log.warn(traceback.format_exc())
            continue

    if sales:
        embed = Embed(
            title = 'Mes produits',
            description = "Voici la liste des articles que vous avez créés. Sélectionnez un article pour le modifier ou le publier",
            color = COLOR
        )
        view = View(timeout = None).add_item(
            Select(
                placeholder = "Choisir un article",
                options = [
                    SelectOption(
                        label = item.name,
                        description = f"{item.price} π ・ {item.description[:30]}...",
                        value = item.id,
                        emoji = Emoji.lock.value if not await item.message else Emoji.world.value
                    )
                    for item in sales
                ],
                custom_id = f"SELECTITEM"
            )
        )
    
    else:
        embed = Embed(
            title = "Mes produits",
            description = f"Vous n'avez encore créé aucun article. Utilisez la commande {Command.ventes_add} pour créer un article.",
            color = COLOR
        )
        view = View()
    
    return embed, view

async def item_card_view(item: CommunityItem):
    guild = client.get_guild(GUILD_ID)
    embed = Embed(
        title = "À vendre",
        description = f"""# {item.name}\n{item.description}\n\n### **{item.price} π**""",
        color = COLOR
    ).set_author(
        name = guild.get_member(item.seller_id).display_name,
        icon_url = guild.get_member(item.seller_id).display_avatar.url
    ).set_footer(
        text = f"{'Frais de ports inclus' if item.fees == "included" else "Frais de ports à régler en Euro"} ・ {'Paiment OnChain' if item.payment_method == "onchain" else 'Paiement Discord' if item.payment_method == "discord" else "Paiement OnChain ou Discord"}"
    ).set_image(
        url = "attachment://image.png"
    )
    view = View(timeout=None).add_item(
        Button(
            label = "Acheter",
            emoji = Emoji.shop_bag.value,
            style = ButtonStyle.green,
            custom_id = f"BUYITEM#{item.id}"
        )
    )
    return embed, view, File(f"data/business/images/{item.id}.png", "image.png") if os.path.exists(f"data/business/images/{item.id}.png") else None

def discord_pre_payout(item: CommunityItem):
    embed = Embed(
        title = "Confirmer l'achat ?",
        description = f"Vous allez utiliser le solde de votre wallet Discord pour acheter {item.name} à {item.price} π.",
        color = COLOR
    )
    view = View(timeout = None).add_item(
        Button(
            label = "Annuler",
            custom_id = "DESTROY",
        )
    ).add_item(
        Button(
            label = "Confirmer",
            custom_id = f"CONFIRMBUY#discord#{item.id}",
            style = ButtonStyle.green,
            emoji = Emoji.shop_bag.value
        )
    )
    return embed, view

def onchain_pre_payout(item: CommunityItem):
    embed = Embed(
        title = "Confirmer l'achat ?",
        description = f"Vous allez utiliser la blockchain pour acheter {item.name} à {item.price} π.\nLorsque vous aurez confirmé, {client.user.display_name} préviendra {item.seller.display_name} de votre réservation. Il ne vous restera plus qu'à effectuer une transaction de {item.price} π vers le wallet de {item.seller.display_name}.",
        color = COLOR
    )
    view = View(timeout = None).add_item(
        Button(
            label = "Annuler",
            custom_id = "DESTROY",
        )
    ).add_item(
        Button(
            label = "Confirmer",
            custom_id = f"CONFIRMBUY#onchain#{item.id}",
            style = ButtonStyle.green,
            emoji = Emoji.shop_bag.value
        )
    )
    return embed, view

async def delete_view(item: CommunityItem):
    embed = Embed(
        title = "Supprimer le produit ?",
        description = "Voulez-vous vraiment supprimer ce produit ? Cette action est irreversible.",
        color = COLOR
    )
    view = View(timeout = None).add_item(
        Button(
            label = "Annuler",
            custom_id = f"BACKITEMID#{item.id}",
            emoji = Emoji.back.value
        )
    ).add_item(
        Button(
            label = "Supprimer",
            custom_id = f"CONFIRMDELETEITEM#{item.id}",
            style = ButtonStyle.red,
            emoji = Emoji.delete.value
        )
    )
    return embed, view
            
async def signin_view():
    embed = Embed(
        title = "Commerce Pi Network",
        description = """
# Vendre et acheter avec ses Pi
Inscrivez vous en tant qu'acheteur ou vendeur pour enrichir votre expérience autour de Pi Network.
## En tant qu'acheteur
Vous pouvez participer aux enchères et acheter des produits mis en vente sur Discord. Vous pouvez payer via votre wallet Mainnet ou Discord.
## En tant que vendeur
Vous recevez tous les privilèges d'acheteur, en plus du droit de créer des enchères, et de mettre en vente des articles sur Discord. Vous choisissez les modalités de paiement et d'envoi des produits physiques.

> Les inscriptions sont soumises aux conditions de services. Consultez les [conditions de vente](https://swakraft.hopto.org/pilabs/terms) et la [charte du vendeur](https://swakraft.hopto.org/pilabs/guidelines). Nécessite un profil Pi vérifié sur le serveur.
""".strip(),
        color = COLOR
    )
    view = View(timeout = None).add_item(
        Button(
            label = "Devenir Vendeur",
            style = ButtonStyle.blurple,
            emoji = Emoji.store.value,
            custom_id = "BECOME_SELLER",
        )
    ).add_item(
        Button(
            label = "Devenir Acheteur",
            emoji = Emoji.cart.value,
            custom_id = "BECOME_BUYER",
        )
    )
    return embed, view
