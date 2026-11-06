import traceback
from init import client, interaction_handler
from chauff_cmn.logging import logger as log
from discord import Interaction
from ..interactions.ticket import register_ticket_interactions
log.info("Registered on_interaction")


register_ticket_interactions()

@client.event
async def on_interaction(interaction: Interaction):
    if not interaction.data:
        return

    interaction_id = interaction.data.get('custom_id')
    values = interaction.data.get('values', [])
    if isinstance(interaction_id, str) and isinstance(values, list):
        try:
            await interact(interaction, interaction_id, values)

        except:
            log.warning(traceback.format_exc())


async def interact(interaction: Interaction, interaction_id: str, values: list[str]):
    log.debug(interaction.user.display_name, interaction_id)
    await interaction_handler.handle_interaction(interaction_id, interaction, values)