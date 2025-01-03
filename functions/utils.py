import aiofiles
from typing import TYPE_CHECKING, Literal, Union
from json import loads, dumps
from discord import Message, PermissionOverwrite, User, Member
from init import BUYER_ROLE_ID, GUILD_ID, SELLER_ROLE_ID, SIGNIN_TICKET_CATEGORY_ID, client
from discord import channel
from discord.utils import get

async def read_file(name: str) -> Union[str, list, dict[str, int | str | bool | dict]]:
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

    return guild.get_role(SELLER_ROLE_ID) in user.roles

def is_buyer(user: User | Member) -> bool:
    guild = client.get_guild(GUILD_ID)
    if isinstance(user, User):
        user = guild.get_member(user.id)
    
    return guild.get_role(BUYER_ROLE_ID) in user.roles
    
async def get_user_signin_channel(user: Member) -> tuple[channel.TextChannel, Message] | tuple[None, None]:
    data: dict[str, int] = await read_file("business/signin_channels.json")
    channel_id = data.get(str(user.id), {}).get("channel_id")
    message_id = data.get(str(user.id), {}).get("message_id")
    try:
        if channel_id:
            channel = client.get_channel(channel_id)
            if channel:
                return channel, await client.get_channel(channel_id).fetch_message(message_id)
            
            return None, None

    except:
        return None, None
        
async def create_user_signin_channel(user: Member, mode: Literal['vendeur', 'acheteur']):
    current_channel, current_message = await get_user_signin_channel(user)
    if not current_channel or not current_message:
        channel = await user.guild.create_text_channel(
            name = user.display_name,
            reason = f"Inscription {mode}",
            category = get(user.guild.categories, id = SIGNIN_TICKET_CATEGORY_ID),
            overwrites = {
                user.guild.default_role: PermissionOverwrite(read_messages = False),
                user: PermissionOverwrite(read_messages = True)
            },
            topic = f"Ce salon a été généré pour suivre votre inscription en tant que {mode}. Vous pouvez demander de l'aide ici en cas de besoin",
        )
        return channel, None

    else:
        return current_channel, current_message

async def mark_as_done(user: Member):
    data = await read_file("business/signin_channels.json")
    data[str(user.id)]['done'] = True
    await write_file("business/signin_channels.json", data)