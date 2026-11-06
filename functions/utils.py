from discord import Message, TextChannel
from init import client


async def fetch(channel_id: int, message_id: int) -> Message:
    channel = client.get_channel(channel_id)
    if channel is None:
        raise ValueError(f"Channel with ID {channel_id} not found.")
    assert isinstance(channel, TextChannel)
    return await channel.fetch_message(message_id)
