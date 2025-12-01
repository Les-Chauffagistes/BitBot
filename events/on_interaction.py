import traceback
from init import client, log
from discord import Interaction
from interactions_bus import bitcoin, utils
from asyncio import gather

log.info("Registered on_interaction")

@client.event
async def on_interaction(interaction: Interaction):
    if not interaction.data:
        return
    
    if 'custom_id' in interaction.data:
        id = interaction.data['custom_id']
        if 'values' in interaction.data:
            values = interaction.data['values']
        
        else:
            values = []
        
        try:
            await interact(interaction, id, values)
        
        except:
            log.warn(traceback.format_exc())

async def interact(interaction: Interaction, id: str, values: list[str]):
    log.debug(interaction.user.display_name, id)
    buses = [utils, bitcoin]
    await gather(*[bus.interact(interaction, id, values) for bus in buses])