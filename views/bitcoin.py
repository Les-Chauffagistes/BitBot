import asyncio
import os
from discord import Embed, File
from classes.emoji import Emoji
from init import COLOR, log
from modules.opennode.model.charge import Charge
from modules.opennode.model.withdraw_request import Withdraw_request

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask
from discord.ui import View, Button

def test():
    qr = qrcode.QRCode(error_correction=qrcode.ERROR_CORRECT_H)
    print('Writing data...')
    qr.add_data('lightning:lnbc100n1pntvfsxpp58u3k03j4jvz7rzctwxlt83cmpqqkdyd4503a74tar97x98uq2ymsdq9fch5zcqzzsxqyz5vqsp5l72t8pkh7sfj6mzvtxv6hyq7kfg4yptferzkxr4yvul70ajrwqmq9qyyssq485zwe02tku8r7665jf9ehp2rd4qs6vg9h38keldp90rdxen5n45vz34sxe79n0n5fjxhescnzm6ydtgyknfy0q2pkmqmfr7vga4gscpv2c068')

    border = (0, 0, 0)
    center = (70, 46, 12)
    print('Generating...')
    img_3 = qr.make_image(image_factory=StyledPilImage, embeded_image_path="assets/brand_icon_round.png", module_drawer = RoundedModuleDrawer(), color_mask=RadialGradiantColorMask(center_color = center, edge_color = border))
    print("saving...")
    img_3.save("output/output3.png")

def make_qr_code(invoice: Charge | Withdraw_request):
    if isinstance(invoice, Charge):
        data = invoice.payreq
    
    elif isinstance(invoice, Withdraw_request):
        data = invoice.lnurl

    qr = qrcode.QRCode(error_correction = qrcode.ERROR_CORRECT_H)
    log.info("adding data")
    qr.add_data(f"lightning:{data}")
    border = (0, 0, 0)
    center = (70, 46, 12)
    log.debug("generating")
    img_3 = qr.make_image(
        image_factory = StyledPilImage,
        embeded_image_path = "assets/brand_icon_round.png",
        module_drawer = RoundedModuleDrawer(),
        color_mask = RadialGradiantColorMask(
            center_color = center,
            edge_color = border
        )
    )
    log.debug("done")
    img_3.save(f"output/{data[0:10]}.png")

async def payment_view(charge: Charge):
    embed = Embed(
        title = "Déposer du Bitcoin",
        description = "Scannez ce QR Code avec un wallet Lightning pour déposer.\n\nImpossible de scanner ? Appuyez sur Obtenir le LNURL et copiez le lien.",
        color = COLOR
    ).set_image(
        url = "attachment://invoice.png"
    ).set_footer(
        text = "L'invoice expire dans 24h"
    )
    loop = asyncio.get_running_loop()
    log.debug("Performing en thread...")
    await loop.run_in_executor(None, make_qr_code, charge)
    log.debug("Exiting thread...")
    file = File(f'output/{charge.payreq[0:10]}.png', 'invoice.png')
    custom_id = os.urandom(16).hex()
    await charge.bind(custom_id) # bind lnurl with button id
    view = View(timeout = None).add_item(
        Button(
            label = "Obtenir le LNURL",
            custom_id = f"LNURL#{custom_id}",
            emoji = Emoji.json.value
        )
    )
    return embed, view, file

async def withdraw_view(withdraw: Withdraw_request):
    embed = Embed(
        title = "Retirer du Bitcoin",
        description = "Scannez ce QR Code avec un wallet Lightning pour retirer.\n\nImpossible de scanner ? Appuyez sur Obtenir le LNURL et copiez le lien.",
        color = COLOR
    ).set_image(
        url = "attachment://invoice.png"
    )
    loop = asyncio.get_running_loop()
    log.debug("Performing en thread...")
    await loop.run_in_executor(None, make_qr_code, withdraw)
    log.debug("Exiting thread...")
    file = File(f'output/{withdraw.lnurl[0:10]}.png', 'invoice.png')
    custom_id = os.urandom(16).hex()
    await withdraw.bind(custom_id) # bind lnurl with button id
    view = View(timeout = None).add_item(
        Button(
            label = "Obtenir le LNURL",
            custom_id = f"LNURL#{custom_id}",
            emoji = Emoji.json.value
        )
    )
    return embed, view, file