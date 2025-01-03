import traceback
from discord import Message, Embed
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

    except:
        log.warn(traceback.format_exc())