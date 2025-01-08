from discord import Interaction


async def interact(interaction: Interaction, id: str, values: list[str]):
    match id.split("#")[0]:
        case "PRINT":
            await interaction.response.send_message(
                content = id.split("#")[1]
            )