from math import e
import os
from socket import timeout
from typing import Optional
from discord import ButtonStyle, ChannelType, Embed, File, SelectOption, TextStyle
from classes.emoji import Emoji
from classes.item import AdminItem
from discord.ui import Modal, TextInput, View, Button, Select, TextInput
from init import COLOR, GUILD_ID, SHOP_CATEGORY, client
from discord.utils import get

def item_modal(item: AdminItem | None):
    modal = Modal(title = "Modifier le produit" if item else "Créer un produit")
    raw_title = TextInput(
        label = "Nom du produit",
        placeholder = "Superbe boule de pétanque",
        default = item.name if item else None
    )
    raw_description = TextInput(
        label = "Description du produit",
        placeholder = "Balle ronde et grise",
        style = TextStyle.long,
        default = item.description if item else None
    )
    modal.add_item(raw_title).add_item(raw_description)
    return modal, raw_title, raw_description

def build_variantes_select(item: AdminItem, selected_variante: Optional[AdminItem.Variante]):
    options: list[SelectOption] = []
    for variante in item.variantes:
        if variante.promo:
            description = f"❌ {variante.price} π ✅ {variante.promo} π"
        
        else:
            description = f"{variante.price} π"
        
        description += f" ・ {variante.description}"

        options.append(
            SelectOption(
                label = f"{variante.name}",
                description = description,
                value = variante.id,
                default = variante == selected_variante if selected_variante else False,
            )
        )

    options.append(
        SelectOption(
            label = "Nouvelle variante",
            description = "Créer une nouvelle variante de l'objet",
            value = "NEW"
        )
    )

    return options

async def item_view(item: AdminItem):
    embed = Embed(
        title = "Modifier le produit",
        description = f"# {item.name}\n{item.description}",
        color = COLOR
    ).set_image(
        url = "attachment://image.png"
    )
    if os.path.exists("data/business/images/" + str(item.id) + ".png"):
        file = File(f"data/business/images/{item.id}.png", "image.png")
    
    else:
        file = None

    view = View(timeout = None).add_item(
        Button(
            label = "Modifier le produit",
            emoji = Emoji.edit.value,
            custom_id = f"BUSINESSEDITITEM#{item.id}"
        )
    )
    
    if not await item.message:
        view.add_item(
            Button(
                label = "Publier",
                style = ButtonStyle.success,
                emoji = Emoji.world.value,
                custom_id = f"BUSINESSPUBLISHITEM#{item.id}"
            )
        )
    
    else:
        view.add_item(
            Button(
                label = "Supprimer",
                style = ButtonStyle.danger,
                emoji = Emoji.delete.value,
                custom_id = f"BUSINESSDELETEITEM#{item.id}"
            )
        )

    view.add_item(
        Select(
            placeholder = "Variantes",
            options = build_variantes_select(item, None),
            custom_id = f"BUSINESSSELECTVARIANTEID#{item.id}"
        )
    )
    return embed, view, file

def item_variante_modal(item: AdminItem, variante: Optional[AdminItem.Variante]):
    modal = Modal(title = f"Créer une variante de {item.name}")
    raw_name = TextInput(
        label = "Nom de la variante",
        placeholder = "Carte de 50€",
        default = variante.name if variante else "",
    )
    raw_description = TextInput(
        label = "Description (faculatitf)",
        placeholder = "Rechargez votre compte avec cette carte d'une valeur de 50€",
        default = variante.description if variante else "",
        required = False
    )
    raw_price = TextInput(
        label = "Prix",
        placeholder = "300",
        default = variante.price if variante else ""
    )
    raw_promo = TextInput(
        label = "Prix promotionnel",
        placeholder = "280",
        default = variante.promo if variante else "",
        required = False
    )
    modal.add_item(raw_name).add_item(raw_description).add_item(raw_price).add_item(raw_promo)
    return modal, raw_name, raw_description, raw_price, raw_promo

def item_variante_view(item: AdminItem, variante: AdminItem.Variante):
    if variante.promo:
        price_line = f"~~{variante.price} π~~ **{variante.promo} π**"
    
    else:
        price_line = f"{variante.price} π"

    embed = Embed(
        title = f"Modifier une variante de {variante.item.name}",
        description = f"## {variante.name}\n{variante.description}\n### {price_line}",
        color = COLOR
    )

    options = build_variantes_select(item, variante)
    view = View(timeout = None).add_item(
        Button(
            label = "Modifier la variante",
            emoji = Emoji.edit.value,
            custom_id = f"BUSINESSEDITITEMVARIANTE#{variante.item.id}#{variante.id}"
        )
    ).add_item(
        Button(
            label = "Supprimer la variante",
            emoji = Emoji.delete.value,
            custom_id = "BUSINESSDELETEITEMVARIANTE#" + str(variante.item.id) + "#" + str(variante.id),
            style = ButtonStyle.danger
        )
    ).add_item(
        Select(
            placeholder = "Variantes",
            options = options,
            custom_id = f"BUSINESSSELECTVARIANTEID#{item.id}"
        )
    ).add_item(
        Button(
            label = "Retour",
            emoji = Emoji.back.value,
            custom_id = f"BUSINESSSELECTIEM#{variante.item.id}",
            row = 2
        )
    )
    if os.path.exists(f"data/business/images/{variante.item.id}.png"):
        file = File(f"data/business/images/{variante.item.id}.png", "image.png")

    else:
        file = None

    return embed, view, file

def select_channel(item: AdminItem):
    options: list[SelectOption] = []
    category = get(client.get_guild(GUILD_ID).categories, id = SHOP_CATEGORY)
    for channel in category.channels[0:25]:
        options.append(
            SelectOption(
                label = channel.name,
                value = channel.id,
                description = channel.topic
            )
        )

    view = View(timeout = None)
    
    if not options == []:
        view.add_item(
            Select(
                placeholder = "Salons...",
                options = options,
                custom_id = f"BUSINESSSELECTCHANNEL#{item.id}"
            )
        )
        embed = Embed(
            title = "Choisir un salon pour le produit",
            description = "Publiez le produit dans le salon de votre choix",
            color = COLOR
        )
    
    else:
        embed = Embed(
            title = "Aucun salon disponible",
            description = "Veuillez créer un salon pour publier le produit",
            color = COLOR
        )
    
    view.add_item(
        Button(
            label = "Retour",
            custom_id = "BUSINESSSELECTIEM#" + str(item.id),
            emoji = Emoji.back.value
        )
    )
    
    return embed, view

async def product_view(item: AdminItem):
    embed = Embed(
        title = "Boutique Fulcran",
        description = f"# {item.name}\n{item.description}\n\n{len(item.variantes)} options, à partir de {item.min_price} π",
        color = COLOR
    ).set_image(
        url = "attachment://image.png"
    )
    view = View(timeout = None).add_item(
        Button(
            label = "Acheter",
            emoji = Emoji.shop_bag.value,
            custom_id = f"BUYBUSINESSSHOPITEM#{item.id}",
            style = ButtonStyle.green
        )
    )
    if os.path.exists(f"data/business/images/{item.id}.png"):
        file = File(f"data/business/images/{item.id}.png", "image.png")
    
    else:
        file = None

    return embed, view, file

def select_variante_purchase_view(item: AdminItem):
    embed = Embed(
        title = "Choisir une option",
        description = f"Choisissez une option pour {item.name}",
        color = COLOR
    )
    options = build_variantes_select(item, None)
    del options[-1]
    view = View(timeout = None).add_item(
        Select(
            placeholder = "Options",
            options = options,
            custom_id = f"BUSINESSSELECTPURCHASEITEM#{item.id}"
        )
    )
    return embed, view

def preview_item_variant(item: AdminItem, variante: AdminItem.Variante):
    if variante.promo:
        price_line = f"~~{variante.price} π~~ **{variante.promo} π**"
    
    else:
        price_line = f"{variante.price} π"

    embed = Embed(
        title = f"",
        description = f"# {item.name}\n{item.description}\n## {variante.name}\n{variante.description}\n### {price_line}",
        color = COLOR
    )

    options = build_variantes_select(item, variante)
    del options[-1]
    view = View(timeout = None).add_item(
        Select(
            placeholder = "Options",
            options = options,
            custom_id = f"BUSINESSSELECTPURCHASEITEM#{item.id}"
        )
    ).add_item(
        Button(
            label = "Tout compte fait, non",
            emoji = Emoji.back.value,
            custom_id = "DESTROY",
        )
    ).add_item(
        Button(
            label = "Acheter",
            emoji = Emoji.shop_bag.value,
            custom_id = f"BUSINESSPURCHASEITEM#{item.id}#{variante.id}",
            style = ButtonStyle.green
        )
    )
    return embed, view

def confirm_payment_view(item: AdminItem, variante: AdminItem.Variante):
    embed = Embed(
        title = "Confirmer l'achat",
        description = f"Voulez-vous utiliser votre solde π sur Discord pour acheter **{item.name} : {variante.name}** pour **{variante.user_price} π** ?",
        color = COLOR
    )
    view = View(timeout = None).add_item(
        Button(
            label = "Annuler",
            custom_id = "DESTROY",
            style = ButtonStyle.danger
        )
    ).add_item(
        Button(
            label = "Confirmer",
            emoji = Emoji.shop_bag.value,
            custom_id = f"BUSINESSCONFIRMPAYMENT#{item.id}#{variante.id}",
            style = ButtonStyle.green
        )
    )
    return embed, view