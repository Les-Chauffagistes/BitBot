import aiofiles, re
from typing import Any, Optional, Union, cast
from json import loads, dumps
from discord import Embed, Guild, Message, TextChannel, User, Member
from init import ADMIN_NOTIFICATIONS_CHANNEL_ID, COLOR, GUILD_ID, client, log

async def read_file(name: str) -> Any:
    """
    Read file in data directory
    """
    async with aiofiles.open(f'data/{name}', 'r') as async_readable_file:
        content = await async_readable_file.read()
        await async_readable_file.close()
        if name.endswith('.json'):
            return loads(content)
        
        return content

async def write_file(name: str, data: Union[str, list, dict]) -> None:
    """
    Write file in data directory
    """
    async with aiofiles.open(f'data/{name}', 'w') as async_writable_file:
        if isinstance(data, (dict, list)):
            await async_writable_file.write(dumps(data, indent = 4))
        
        else:
            await async_writable_file.write(data)
        
        await async_writable_file.close()
    
async def fetch(channel_id: int, message_id: int) -> Message:
    channel = client.get_channel(channel_id)
    assert channel is not None
    assert isinstance(channel, TextChannel)
    return await channel.fetch_message(message_id)

def is_manager(user: Union[User, Member]) -> bool:
    if isinstance(user, User):
        guild = cast(Guild, client.get_guild(GUILD_ID))
        retrieved_user = guild.get_member(user.id)
        if not retrieved_user:
            return False
        
        user = retrieved_user

    return not set([role.id for role in user.roles]).isdisjoint([1313062024200327238])
        
async def send_admin(title: str, description: str, member: Optional[Member | User] = None, silent: bool = False):
    channel = client.get_channel(ADMIN_NOTIFICATIONS_CHANNEL_ID)
    assert isinstance(channel, TextChannel)
    embed = Embed(
        title = title,
        description = description,
        color = COLOR
    )
    if member:
        embed.set_author(
            name = member.display_name,
            icon_url = member.display_avatar.url
        )
        
    await channel.send(
        embed = embed,
        silent = silent
    )

def from_string_to_number(value: str) -> float:
    if re.match("^\\d+$", value):
        return float(value)
    decimal_value = float(value[0:-1])
    suffix = value[-1].upper()
    match suffix:
        case "T":
            decimal_value *= 1e12

        case "G":
            decimal_value *= 1e9

        case "M":
            decimal_value *= 1e6

        case "K":
            decimal_value *= 1e3
        
        case _:
            raise ValueError("Unknown suffix")
    
    return round(decimal_value)


def from_number_to_string(value: float) -> str:
    def try_round(value: float | int):
        if round(value) == value:
            return int(value)
        return f"{value:.2f}"
    
    if value < 1e3:
        return f"{value}"
    elif value < 1e6:
        return f"{try_round(value / 1e3)} K"
    elif value < 1e9:
        return f"{try_round(value / 1e6)} M"
    elif value < 1e12:
        return f"{try_round(value / 1e9)} G"
    elif value < 1e15:
        return f"{try_round(value / 1e12)} T"
    elif value < 1e18:
        return f"{try_round(value / 1e15)} P"
    else:
        return f"{try_round(value / 1e18)} E"