import traceback
from init import log, COLOR
from discord.app_commands import Group, allowed_contexts, allowed_installs
from discord import Interaction, Embed
from modules.chauffagistes.api import get_infos 
from functions.utils import from_number_to_string



pool = Group(name = "pool", description = "Commandes d'accès à la pool Les Chauffagistes")

@allowed_installs(
    guilds=True,
    users=True
)
@allowed_contexts(
    guilds=True,
    dms=True,
    private_channels=True,
)
@pool.command(
    name = "stats",
    description = "Globales de la pool"
)
async def pool_command(interaction: Interaction):
    try:
        data = await get_infos()
        log.debug(data)

        description = f"""
**{data["pool"]["runtime"]["Users"]}** utilisateurs
**{data["pool"]["runtime"]["Workers"]}** workers ({data["pool"]["runtime"]["Idle"]} inactifs, {data["pool"]["runtime"]["Disconnected"]} hors-ligne)
## Hashrates
1 min: `{data["pool"]["hashrates"]["hashrate1m"]}H/s`
1 h: `{data["pool"]["hashrates"]["hashrate1hr"]}H/s`
1 j: `{data["pool"]["hashrates"]["hashrate1d"]}H/s`
7 j: `{data["pool"]["hashrates"]["hashrate7d"]}H/s`
## Shares
Diff: {data["pool"]["shares"]["diff"]}
{from_number_to_string(data["pool"]["shares"]["accepted"])} acceptés, {from_number_to_string(data["pool"]["shares"]["rejected"])} rejettés
Best share: {from_number_to_string(data["pool"]["shares"]["bestshare"])}
Shares par seconde: {data["pool"]["shares"]["SPS1m"]}
""".strip()

        await interaction.response.send_message(
            embed = Embed(
                title = "Stats globales",
                description = description,
                color = COLOR
            )
        )

    except Exception:
        log.warn(traceback.format_exc())