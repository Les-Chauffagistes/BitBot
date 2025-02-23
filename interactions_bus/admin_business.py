import traceback
from discord import Embed, Interaction
from classes.brand import Brand
from init import COLOR, log
from views.admin_business import admin_card_modal_edit, brand_card_edit, brand_main_admin, brand_main_edit, card_add_code_modal, card_codes_view, card_confirm_delete_code

async def interact(interaction: Interaction, id: str, values: list[str]):
    match id.split("#")[0]:
        case "ADMINSELECTBRAND":
            brand_id = int(values[0])
            brand = await Brand.from_id(brand_id)
            embed, view = await brand_main_edit(brand)
            await interaction.response.edit_message(
                embed = embed,
                view = view
            )
        
        case "ADMINBACKTOMAINBRANDEDIT":
            embed, view = await brand_main_admin()
            await interaction.response.edit_message(
                embed = embed,
                view = view
            )
        
        case "ADMINADDNEWCARD":
            brand_id = int(id.split("#")[1])
            brand = await Brand.from_id(brand_id)
            modal, raw_name, raw_value, raw_price, raw_promo_price = admin_card_modal_edit(None)
            async def handle_new_card(interaction2: Interaction):
                try:
                    name = raw_name.value.strip()
                    value = raw_value.value.strip()
                    price = raw_price.value.strip()
                    promo_price = raw_promo_price.value.strip()

                    int_value, int_price, int_promo_price = 0, 0, 0

                    message = ""
                    if value.isdecimal():
                        int_value = int(value)
                    
                    else:
                        message = "La valeur du prix doit être un entier"
                    
                    if price.isdecimal():
                        int_price = int(price)
                    
                    else:
                        message = "Le prix doit etre un entier"
                    
                    if promo_price.isdecimal() or promo_price == "":
                        if promo_price == "":
                            int_promo_price = None

                        else:
                            int_promo_price = int(promo_price)
                        
                    else:
                        message = "Le prix promotionnel doit etre un entier"
                    
                    if message != "":
                        await interaction2.response.send_message(
                            embed = Embed(
                                title = "Erreur de saisie",
                                description = message,
                                color = COLOR
                            ),
                            ephemeral = True
                        )
                        return

                    await brand.add_card(interaction2.id,name, int_value, int_price, int_promo_price)
                    embed, view = await brand_main_edit(brand)
                    await interaction2.response.edit_message(
                        embed = embed,
                        view = view
                    )
                
                except:
                    log.warn(traceback.format_exc())

            modal.on_submit = handle_new_card
            await interaction.response.send_modal(modal)
        
        case "SELECTCARD":
            brand_id = int(id.split("#")[1])
            brand = await Brand.from_id(brand_id)
            card_id = int(values[0])
            card = brand.get_card(card_id)
            if card:
                embed, view = await brand_card_edit(brand, card)
                await interaction.response.edit_message(
                    embed = embed,
                    view = view
                )
        
        case "ADMINEDITCARD":
            brand_id = int(id.split("#")[1])
            brand = await Brand.from_id(brand_id)
            card_id = int(id.split("#")[2])
            card = brand.get_card(card_id)
            if card:
                modal, raw_name, raw_value, raw_price, raw_promo_price = admin_card_modal_edit(card)
                async def handle_edit_card(interaction2: Interaction):
                    try:
                        name = raw_name.value.strip()
                        value = raw_value.value.strip()
                        price = raw_price.value.strip()
                        promo_price = raw_promo_price.value.strip()

                        int_value, int_price, int_promo_price = 0, 0, 0

                        message = ""
                        if value.isdecimal():
                            int_value = int(value)
                        
                        else:
                            message = "La valeur du prix doit être un entier"
                        
                        if price.isdecimal():
                            int_price = int(price)
                        
                        else:
                            message = "Le prix doit etre un entier"
                        
                        if promo_price.isdecimal() or promo_price == "":
                            if promo_price == "":
                                int_promo_price = None

                            else:
                                int_promo_price = int(promo_price)
                            
                        else:
                            message = "Le prix promotionnel doit etre un entier"
                        
                        if message != "":
                            await interaction2.response.send_message(
                                embed = Embed(
                                    title = "Erreur de saisie",
                                    description = message,
                                    color = COLOR
                                ),
                                ephemeral = True
                            )
                            return

                        await card.edit(name, int_value, int_price, int_promo_price)
                        embed, view = await brand_card_edit(brand, card)
                        await interaction2.response.edit_message(
                            embed = embed,
                            view = view
                        )
                    
                    except:
                        log.warn(traceback.format_exc())

                modal.on_submit = handle_edit_card
                await interaction.response.send_modal(modal)
            
        case "ADMINBACKTOCARDEDIT":
            brand_id = int(id.split('#')[1])
            brand = await Brand.from_id(brand_id)
            embed, view = await brand_main_edit(brand)
            await interaction.response.edit_message(
                embed = embed,
                view = view
            )
        
        case "ADMINMANAGECODES":
            brand_id = int(id.split("#")[1])
            brand = await Brand.from_id(brand_id)
            card_id = int(id.split("#")[2])
            card = brand.get_card(card_id)
            if card:
                embed, view = card_codes_view(brand, card)
                await interaction.response.edit_message(
                    embed = embed,
                    view = view
                )

        case "BACKTOCARDEDIT":
            brand_id = int(id.split("#")[1])
            brand = await Brand.from_id(brand_id)
            card_id = int(id.split("#")[2])
            card = brand.get_card(card_id)
            if card:
                embed, view = await brand_card_edit(brand, card)
                await interaction.response.edit_message(
                    embed = embed,
                    view = view
                )
            
        case "CARDADDCODE":
            brand_id = int(id.split("#")[1])
            brand = await Brand.from_id(brand_id)
            card_id = int(id.split("#")[2])
            card = brand.get_card(card_id)
            if card:
                modal, raw_code = card_add_code_modal()
                async def handle_code(interaction2: Interaction):
                    try:
                        code = raw_code.value.strip()
                        if len(code) != 0:
                            await card.add_code(code)
                            embed, view = card_codes_view(brand, card)
                            await interaction2.response.edit_message(
                                embed = embed,
                                view = view
                            )
                        
                        else:
                            await interaction2.response.send_message(
                                embed = Embed(
                                    title = "Code invalide",
                                    description = "Le code trop court",
                                    color = COLOR
                                ),
                                ephemeral = True 
                            )
                    
                    except:
                        log.warn(traceback.format_exc())
                
                modal.on_submit = handle_code
                await interaction.response.send_modal(modal)
            
        case "DELETECARDCODE":
            brand_id = int(id.split("#")[1])
            brand = await Brand.from_id(brand_id)
            card_id = int(id.split("#")[2])
            card = brand.get_card(card_id)
            if card:
                embed, view = card_confirm_delete_code(brand, card, values[0])
                await interaction.response.edit_message(
                    embed = embed,
                    view = view
                )

        
        case "CARDCONFIRMDELETECODE":
            brand_id = int(id.split("#")[1])
            brand = await Brand.from_id(brand_id)
            card_id = int(id.split("#")[2])
            card = brand.get_card(card_id)
            code = id.split("#")[3]
            if card:
                try:
                    await card.remove_code(code)
                    embed, view = card_codes_view(brand, card)
                    await interaction.response.edit_message(
                        embed = embed,
                        view = view
                    )
                
                except brand.CardError:
                    await interaction.response.send_message(
                        embed = Embed(
                            title = "Code introuvable",
                            description = "Le code a peut être été supprimé",
                            color = COLOR
                        ),
                        ephemeral = True
                    )
                