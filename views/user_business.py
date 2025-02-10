

from discord import ButtonStyle, Embed, Interaction
from discord.ui import View, Select, Button
from classes import emoji
from classes.brand import Brand
from classes.emoji import Emoji
from init import COLOR


async def main_shop_view():
    """Vue principale de la boutique Fulcran"""
    options = await Brand.select_all_brands()
    view = View(timeout = None)
    if options:
        embed = Embed(
            title = "Bienvenue dans la boutique Fulcran",
            description = "Utilisez le menu ci-dessous pour explorer les enseignes",
            color = COLOR
        )
        view.add_item(
            Select(
                placeholder = "Enseignes",
                options = options,
                custom_id = "USERSELECTBRAND"
            )
        )

    else:
        embed = Embed(
            title = "Bienvenue dans la boutique Fulcran",
            description = "Aucune enseigne disponible pour le moment. Veuillez réessayer plus tard",
            color = COLOR
        )
    
    return embed, view

def main_brand_view(brand: Brand):
    """Vue principale d'une enseigne"""
    try:
        start_price_text = f", à partir de {brand.start_price} π"
    
    except Brand.CardError:
        start_price_text = ""

    embed = Embed(
        title = brand.name,
        description = f"{brand.description}\n\n{len(brand.cards)} options{start_price_text}",
        color = COLOR
    )
    view = View(timeout = None)
    if brand.cards:
        view.add_item(
            Select(
                placeholder = "Options d'achat",
                options = brand.select_all_cards(),
                custom_id = f"USERSELECTCARD#{brand.id}"
            )
        )
    
    view.add_item(
        Button(
            label = "Retour",
            custom_id = "USERBACKTOBRAND",
            emoji = Emoji.back.value
        )
    )

    return embed, view

def card_view(brand: Brand, card: Brand.Card):

    if card.promo_price: price_text = f"~~{card.price} π~~ **{card.promo_price} π**"
    else: price_text = f"{card.price} π"
    
    if card.codes: status = f"Il reste {len(card.codes)} exemplaire{'s' if len(card.codes) > 1 else ''}"
    else: status = "**Rupture de stock**"

    embed = Embed(
        title = brand.name,
        description = f"{brand.description}\n## {card.name}\n\n{price_text}\n{status}",
        color = COLOR
    )

    view = View(timeout = None).add_item(
        Button(
            label = "Retour",
            custom_id = f"BACKTOBRANDID#{brand.id}",
            emoji = Emoji.back.value
        )
    )

    if card.codes:
        view.add_item(
            Button(
                label = "Acheter",
                custom_id = f"BUYCARD#{brand.id}#{card.id}",
                emoji = Emoji.shop_bag.value,
                style = ButtonStyle.green
            )
        )

    return embed, view

def payment_confirm(brand: Brand, card: Brand.Card):
    embed = Embed(
        title = "Confirmation d'achat",
        description = f"Voulez-vous utiliser votre solde Pi Discord pour acheter un produit {brand.name} - **{card.name}** pour **{card.current_price} π** ?",
        color = COLOR
    )
    view = View(timeout = None).add_item(
        Button(
            label = "Annuler",
            custom_id = f"BACKTOCARD#{brand.id}#{card.id}",
            emoji = Emoji.back.value
        )
    ).add_item(
        Button(
            label = "Confirmer l'achat",
            custom_id = f"CONFIRMCARDPAYMENT#{brand.id}#{card.id}",
            emoji = Emoji.shop_bag.value,
            style = ButtonStyle.green
        )
    )

    return embed, view

def shop_public_view():
    embed = Embed(
        title = "Boutique Fulcran",
        description = "Découvrez la boutique Fulcran",
        color = COLOR  
    )
    view = View(timeout = None).add_item(
        Button(
            label = "Entrer",
            style = ButtonStyle.green,
            emoji = Emoji.store.value,
            custom_id = "OPENSHOP"
        )
    )
    return embed, view