from enum import member
import traceback
from typing import Any, cast
from classes.brand import Brand
from functions.utils import read_file
from init import COLOR, GUILD_ID, routes, log, client
from aiohttp.web_request import Request
from aiohttp.web import HTTPOk, json_response
from discord import Guild, Status

log.info("Handler /test defined")
@routes.get('/test')
async def message(request: Request):
    log.debug(await request.json())
    return HTTPOk(body="Success")

@routes.get('/server')
async def server(request: Request):
    """Renvoie les informations sur le serveur discord"""
    guild = cast(Guild, client.get_guild(GUILD_ID))

    return json_response({
        "name": guild.name,
        "members": guild.member_count,
        "online": len([member for member in guild.members if member.status.value != "offline"])
    })

@routes.get('/business/entries')
async def entries(request: Request):
    log.get("business/entries")
    data = cast(dict[str, Brand.HistoryEntry.types], await read_file('business/history.json'))
    result: dict[str, dict] = {}
    for entry_id in data.keys():
        try:
            result[entry_id] = (await Brand.HistoryEntry.load_entry(entry_id)).json #type: ignore
        
        except:
            log.warn(traceback.format_exc())
            continue
    
    return json_response(result)