import os
from typing import Optional
from discord import ButtonStyle, Embed, File, SelectOption, TextStyle
from classes.emoji import Emoji, ShopEmoji
from classes.item import AdminItem
from discord.ui import Modal, TextInput, View, Button, Select, TextInput
from init import COLOR, GUILD_ID, SHOP_CATEGORY, client, log
from discord.utils import get

def item_modal(item: AdminItem | None):
    modal = Modal(title = "Modifier la boutique" if item else "Ajouter une boutique")
    raw_title = TextInput(
        label = "Nom de la boutique",
        placeholder = "Amazon",
        default = item.name if item else None
    )
    raw_description = TextInput(
        label = "Description de la boutique",
        placeholder = "Tous les articles de Amazon",
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
            label = "Ajouter un article",
            description = "Créer un article pour la boutique",
            value = "NEW"
        )
    )

    return options

async def item_view(item: AdminItem):
    embed = Embed(
        title = "Modifier la boutique",
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
            label = "Modifier la boutique",
            emoji = Emoji.edit.value,
            custom_id = f"BUSINESSEDITITEM#{item.id}"
        )
    ).add_item(
        Button(
            label = "Emoji",
            emoji = item.emoji,
            custom_id = f"BUSINESSEDITEMOJI#{item.id}"
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
            placeholder = "Produits",
            options = build_variantes_select(item, None),
            custom_id = f"BUSINESSSELECTVARIANTEID#{item.id}"
        )
    )
    return embed, view, file

def item_variante_modal(item: AdminItem, variante: Optional[AdminItem.Variante]):
    modal = Modal(title = f"Créer une variante de {item.name}")
    raw_name = TextInput(
        label = "Nom du produit",
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
        title = f"Modifier un produit de {variante.item.name}",
        description = f"## {variante.name}\n{variante.description}\n### {price_line}",
        color = COLOR
    )

    options = build_variantes_select(item, variante)
    view = View(timeout = None).add_item(
        Button(
            label = "Modifier le produit",
            emoji = Emoji.edit.value,
            custom_id = f"BUSINESSEDITITEMVARIANTE#{variante.item.id}#{variante.id}"
        )
    ).add_item(
        Button(
            label = "Supprimer le produit",
            emoji = Emoji.delete.value,
            custom_id = "BUSINESSDELETEITEMVARIANTE#" + str(variante.item.id) + "#" + str(variante.id),
            style = ButtonStyle.danger
        )
    ).add_item(
        Select(
            placeholder = "Produits",
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
            label = "Retour",
            emoji = Emoji.back.value,
            custom_id = "BACKSHOP"
        )
    ).add_item(
        Button(
            label = "Voir les options",
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
    ).add_item(
        Button(
            label = "Retour",
            emoji = Emoji.back.value,
            custom_id = f"SHOPSELECTITEM#{item.id}"
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
            custom_id = "BACKSHOP",
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
            custom_id = f"SHOPSELECTITEM#{item.id}",
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

async def shop_view():
    embed = Embed(
        title = "Boutique Fulcran",
        description = "Consulter la boutique",
        color = COLOR
    )
    view = View(timeout = None).add_item(
        Button(
            label = "Ouvrir la boutique",
            custom_id = "OPENSHOP",
            style = ButtonStyle.blurple
        )
    )
    return embed, view

async def shop_main_view():
    embed = Embed(
        title = "Boutique Fulcran",
        description = "Choisissez un produit",
        color = COLOR
    )
    shop: list[AdminItem] = []
    options : list[SelectOption] = []
    for file in os.listdir("data/business/shop"):
        item = await AdminItem.from_id(file.split(".")[0])
        shop.append(item)
        options.append(
            SelectOption(
                label = item.name,
                description = f"Dès {item.min_price} π - {item.description[:30]}",
                value = item.id,
                emoji = item.emoji
            )
        )

    view = View(timeout = None).add_item(
        Select(
            placeholder = "Produits",
            options = options,
            custom_id = f"FULCRANSHOPSELECTITEM#{shop[-1].id}"
        )
    )
    return embed, view

async def main_edit_view():
    embed = Embed(
        title = "Édition de la boutique Fulcran",
        description = "Sélectionnez une boutique pour la modifier, ou modifier un article de celle ci",
        color = COLOR
    )

    options: list[SelectOption] = []
    for file in os.listdir("data/business/shop"):
        item = await AdminItem.from_id(file.split(".")[0])
        options.append(
            SelectOption(
                label = item.name,
                description = f"Dès {item.min_price} π - {item.description[:30]}",
                value = item.id
            )
        )

    view = View(timeout = None).add_item(
        Select(
            placeholder = "Boutiques",
            options = options,
            custom_id = "ADMINSELECTSHOP"
        )
    )
    return embed, view

async def emoji_select_view(item: AdminItem):
    options: list[SelectOption] = []
    for emoji in ShopEmoji:
        options.append(
            SelectOption(
                label = emoji.name,
                emoji = emoji.value,
                value = emoji.value
            )
        )
    view = View(timeout = None)
    if options:
        embed = Embed(
            title = "Modifier l'emoji",
            description = f"Choisissez un emoji pour {item.name}",
            color = COLOR
        )

        view.add_item(
            Select(
                placeholder = "Emoji",
                options = options,
                custom_id = f"BUSINESSSELECTEMOJI#{item.id}"
            )
        )
    
    else:
        embed = Embed(
            title = "Modifier l'emoji",
            description = f"Aucun emoji disponible sur {client.get_guild(GUILD_ID).name}",
            color = COLOR
        )

    view.add_item(
        Button(
            label = "Retour",
            emoji = Emoji.back.value,
            custom_id = f"BUSINESSSELECTIEM#{item.id}"
        )
    )

    return embed, view