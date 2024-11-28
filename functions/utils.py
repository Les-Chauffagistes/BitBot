import aiofiles
from typing import Union
from json import loads, dumps
from discord import Message, User, Member
from init import GUILD_ID, MODE, client

async def read_file(name: str) -> Union[str, list, dict[str]]:
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
    return await client.get_channel(channel_id).fetch_message(message_id)

def is_manager(user: Union[User, Member]) -> bool:
    return not set([role.id for role in user.roles]).isdisjoint([])

def is_seller(user: User | Member) -> bool:
    guild = client.get_guild(GUILD_ID)
    if isinstance(user, User):
        user = guild.get_member(user.id)

    if MODE == "DEV":
        role = guild.get_role(1310271119466565755)
        return role in user.roles