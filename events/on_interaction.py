import traceback
from init import client, log
from discord import Interaction

@client.event
async def on_interaction(interaction: Interaction):
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
    log.info(interaction.user.display_name, id)
    match id.split['#'][0]:
        case "":
            pass

