import os
from typing import Optional
from discord import ButtonStyle, Embed, File, SelectOption, TextStyle
from classes.emoji import Emoji
from classes.brand import Brand
from discord.ui import Modal, TextInput, View, Button, Select
from init import COLOR, GUILD_ID, client, log
from discord.utils import get

Vue = tuple[Embed, View]

async def brand_main_admin() -> Vue:
    """Le sélecteur principal d'enseignes"""
    options = await Brand.select_all_brands()
    if options:
        embed = Embed(
            title = "Gestion des enseignes",
            description = "Sélectionner un enseigne pour la modifier ou gérer les cartes",
            color = COLOR
        )
        
        view = View(timeout = None).add_item(
            Select(
                placeholder = "Choisir une enseigne",
                options = options,
                custom_id = "ADMINSELECTBRAND"
            )
        )
    
    else:
        embed = Embed(
            title = "Gestion des enseignes",
            description = "Aucune enseigne créée. Créez-en une d'abord.",
            color = COLOR
        )
        view = View()

    return embed, view

async def brand_main_edit(brand: Brand) -> Vue:
    """Vue détaillée d'une enseigne"""
    try:
        start_price_text = f", à partir de {brand.start_price} π"
    
    except Brand.CardError:
        start_price_text = ""

    view = View(timeout = None)
    options = brand.select_all_cards()
    if options:
        embed = Embed(
            title = "Gestion des enseignes",
            description = f"# {brand.name}\n{brand.description}\n{len(brand.cards)} options{start_price_text}\n\nUtilisez le menu pour gérer les différentes cartes de l'enseinge",
            color = COLOR
        )
        view.add_item(
            Select(
                placeholder = "Choisir une carte",
                options = options,
                custom_id = f"SELECTCARD#{brand.id}"
            )
        )
    
    else:
        embed = Embed(
            title = "Gestion des enseignes",
            description = f"# {brand.name}\n{brand.description}\n{len(brand.cards)} options{start_price_text}\n\nAjoutez votre première carte avec le bouton Nouvelle carte",
            color = COLOR
        )

    view.add_item(
        Button(
            label = "Retour",
            custom_id = "ADMINBACKTOMAINBRANDEDIT",
            emoji = Emoji.back.value
        )
    ).add_item(
        Button(
            label = "Nouvelle carte",
            custom_id = f"ADMINADDNEWCARD#{brand.id}",
            emoji = Emoji.add.value,
            style = ButtonStyle.blurple
        )
    )
    
    return embed, view

async def brand_card_edit(brand: Brand, card: Optional[Brand.Card]) -> Vue:
    """Vue détaillée d'une carte"""
    if card:
        if card.promo_price:
            price_text = f"~~{card.price} π~~ **{card.price} π**"
        
        else:
            price_text = f"{card.price} π"

        embed = Embed(
            title = "Gestion des enseignes",
            description = f"# {brand.name}\n{brand.description}\n## {card.name}\n### {price_text}\n{len(card.codes)} disponible{'s' if len(card.codes) > 1 else ''}",
            color = COLOR
        )

        view = View(timeout = None).add_item(
            Select(
                placeholder = "Cartes",
                options = brand.select_all_cards(card.id),
                custom_id = f"SELECTCARD#{brand.id}"
            )
        ).add_item(
            Button(
                label = "Retour",
                custom_id = f"ADMINBACKTOCARDEDIT#{brand.id}", #1
                emoji = Emoji.back.value
            )
        ).add_item(
            Button(
                label = "Modifier",
                custom_id = f"ADMINEDITCARD#{brand.id}#{card.id}",
                emoji = Emoji.edit.value,
                style = ButtonStyle.blurple
            )
        ).add_item(
            Button(
                label = "Gestion des codes",
                custom_id = f"ADMINMANAGECODES#{brand.id}#{card.id}",
                emoji = Emoji.code.value,
                style = ButtonStyle.blurple
            )
        )
        return embed, view
    
    else:
        embed = Embed(
            title = "Gestion des cartes",
            description = f"# {brand.name}\n{brand.description}\nSélectionnez une carte pour la modifier",
        )
        view = View(timeout = None).add_item(
            Select(
                placeholder = "Cartes",
                options = brand.select_all_cards(),
                custom_id = f"SELECTCARD#{brand.id}"
            )
        ).add_item(
            Button(
                label = "Retour",
                custom_id = f"ADMINBACKTOMAINCARDEDIT#{brand.id}",
                emoji = Emoji.back.value
            )
        ).add_item(
            Button(
                label = "Nouvelle carte",
                custom_id = f"ADMINADDNEWCARD#{brand.id}",
                emoji = Emoji.add.value,
                style = ButtonStyle.blurple
            )
        )
        return embed, view
    
def admin_brand_modal_edit(brand: Optional[Brand]):
    if brand:
        modal = Modal(title = "Modifier l'enseigne")
        raw_name = TextInput(
            label = "Nom de l'enseigne",
            placeholder = brand.name,
            default = brand.name
        )
        raw_description = TextInput(
            label = "Description de l'enseigne",
            placeholder = brand.description,
            style = TextStyle.long,
            default = brand.description
        )
        modal.add_item(raw_name).add_item(raw_description)

    else:
        modal = Modal(title = "Nouvelle enseigne")
        raw_name = TextInput(
            label = "Nom de l'enseigne",
            placeholder = "Netflix"
        )
        raw_description = TextInput(
            label = "Description de l'enseigne",
            placeholder = "Une carte cadeau qui va soulager votre carte bancaire",
            style = TextStyle.long,
        )
        modal.add_item(raw_name).add_item(raw_description)

    return modal, raw_name, raw_description

def admin_card_modal_edit(card: Optional[Brand.Card]):
    if card:
        modal = Modal(title = "Modifier la carte")
        raw_name = TextInput(
            label = "Nom de la carte",
            placeholder = card.name,
            default = card.name
        )
        raw_value = TextInput(
            label = "Valeur de la carte (€)",
            placeholder = str(card.value),
            default = str(card.value)
        )
        raw_price = TextInput(
            label = "Prix de vente (Pi)",
            placeholder = str(card.price),
            default = str(card.price)
        )
        raw_promo_price = TextInput(
            label = "Prix de vente promotionnel (Pi)",
            placeholder = str(card.promo_price) if card.promo_price else "",
            default = str(card.promo_price) if card.promo_price else "",
            required = False
        )
        modal.add_item(raw_name).add_item(raw_value).add_item(raw_price).add_item(raw_promo_price)

    else:
        modal = Modal(title = "Nouvelle carte")
        raw_name = TextInput(
            label = "Nom de la carte",
            placeholder = "Carte cadeau de 20€"
        )
        raw_value = TextInput(
            label = "Valeur de la carte (€)",
            placeholder = "1"
        )
        raw_price = TextInput(
            label = "Prix de vente (Pi)",
            placeholder = "230"
        )
        raw_promo_price = TextInput(
            label = "Prix de vente en promo (Pi)",
            placeholder = "200",
            required = False
        )
        modal.add_item(raw_name).add_item(raw_value).add_item(raw_price).add_item(raw_promo_price)
    
    return modal, raw_name, raw_value, raw_price, raw_promo_price

def card_codes_view(brand: Brand, card: Brand.Card) -> Vue:
    codes = card.codes
    total_codes = len(codes)
    embed = Embed(
        title = "Codes d'activation",
        description = f'## {brand.name} - {card.name}\n{total_codes} code{'s' if total_codes > 1 else ''}',
        color = COLOR
    )
    options = [
        SelectOption(
            label = code,
            emoji = Emoji.delete.value
        ) for code in codes
    ]
    view = View(timeout = None)
    if options:
        view.add_item(
            Select(
                placeholder = "Supprimer un code",
                options = options,
                custom_id = f"DELETECARDCODE#{brand.id}#{card.id}"
            )
        )

    view.add_item(
        Button(
            label = "Retour",
            emoji = Emoji.back.value,
            custom_id = f"BACKTOCARDEDIT#{brand.id}#{card.id}"
        )
    ).add_item(
        Button(
            label = "Ajouter",
            emoji = Emoji.add.value,
            custom_id = f"CARDADDCODE#{brand.id}#{card.id}",
            style = ButtonStyle.blurple
        )
    )
    return embed, view

def card_add_code_modal():
    modal = Modal(title = "Nouveau code d'activation")
    raw_code = TextInput(
        label = "Code",
        placeholder = "*****",
        style = TextStyle.long
    )
    modal.add_item(raw_code)
    return modal, raw_code

def card_confirm_delete_code(brand: Brand, card: Brand.Card, code: str) -> Vue:
    embed = Embed(
        title = "Supprimer un code",
        description = "Vouez-vous supprimer ce code d'activation ? Cette action est irreversible.",
        color = COLOR
    )
    view = View(timeout = None).add_item(
        Button(
            label = "Annuler",
            custom_id = f"ADMINMANAGECODES#{brand.id}#{card.id}",
        )
    ).add_item(
        Button(
            label = "Supprimer",
            custom_id = f"CARDCONFIRMDELETECODE#{brand.id}#{card.id}#{code}",
            style = ButtonStyle.red,
            emoji = Emoji.delete.value
        )
    )
    return embed, view