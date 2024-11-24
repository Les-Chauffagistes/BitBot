from typing import Literal, Optional
from discord import ButtonStyle, Embed, Interaction

from classes.discord_wallet import PiWallet
from classes.emoji import Emoji
from classes.item import Item
from init import COLOR, MODE
from discord.ui import View, Button


async def wallet_creation_view(interaction: Interaction, user_wallet: Optional[PiWallet], role: Literal['vendeur', 'acheteur']):
    if not user_wallet:
        embed = Embed(
            title = f"Devenir {role} - Étape 1/3",
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
            title = f"Devenir {role} - Étape 1/3",
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
            title = f"Devenir {role} - Étape 2/3",
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
    if MODE == "DEV":
        role_buyer = interaction.guild.get_role(1310271143168573450)
        role_seller = interaction.guild.get_role(1310271119466565755)
    
    if role == 'acheteur':
        discord_role = role_buyer
    
    else:
        discord_role = role_seller

    if not role in interaction.user.roles:
        embed = Embed(
            title = f"Devenir {role} - Étape 3/3",
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

async def item_edit(interaction: Interaction, item: Optional[Item] = None):
    embed = Embed(
        title = "Gérer le produit",
        description = f"# {item.name}\n{item.description}\n### **{item.price}** Pi",
        color = COLOR
    )
    view = View(timeout = None).add_item(
        Button(
            label= "Modifier la fiche produit",
            emoji = Emoji.edit.value,
            style = ButtonStyle.primary,
            custom_id = f"EDITITEM#{item.id}"
        )
    ).add_item(
        Button(
            label = "Ajouter une image",
            emoji = Emoji.image.value,
            style = ButtonStyle.primary,
            custom_id = f"ADDITEMIMAGE#{item.id}"
        )
    )
    return embed, view