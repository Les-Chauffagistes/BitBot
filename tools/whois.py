from json import loads
import os
from init import GUILD_ID, SELLER_ROLE_ID, client

async def start_check():
    guild = client.get_guild(GUILD_ID)
    role = guild.get_role(SELLER_ROLE_ID)
    members = {}
    for member in guild.members:
        if role in member.roles:
            members[member.id] = {}
            if os.path.exists(f"data/wallets/pi/{member.id}.json"):
                members[member.id]["wallet"] = loads(open(f"data/wallets/pi/{member.id}.json").read())


    return members