import os
import traceback
from discord import Message, Embed
from classes.bitstack.modele.history import History
from init import COLOR, client, log

log.info("Registered on_message")

@client.event
async def on_message(message: Message):
    try:
        if message.author.id == 1088153914823684208:
            if message.content == '.embed':
                await message.delete()
                msg = await message.channel.send(
                    embed = Embed(
                        title = "Chargement",
                        color = COLOR
                    )
                )
                print(f'await fetch({msg.channel.id}, {msg.id})')
        
        for attachement in message.attachments:
            if attachement.filename.endswith(".csv"):
                await attachement.save(f"tmp/csv/{message.author.id}.csv")
                try:
                    history = History.from_csv(f"tmp/csv/{message.author.id}.csv")
                    await message.reply(
                        embed = Embed(
                            title = "Analyse de l'historique",
                            description = f"ROI: {round(await history.ROI * 100, 2)}%\nBitcoin acheté: {round(await history.bitcoin_buyed, 5)}\nFiat dépensé: {round(await history.fiat_sent, 2)} €\nValeur actuelle du portefeuille: {round(await history.wallet_value, 2)} €",
                            color = COLOR
                        )
                    )
                    os.remove(f"tmp/csv/{message.author.id}.csv")
                
                except:
                    continue

    except:
        log.warn(traceback.format_exc())