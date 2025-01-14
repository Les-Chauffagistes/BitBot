from enum import member
from init import COLOR, GUILD_ID, routes, log, client
from aiohttp.web_request import Request
from aiohttp.web import HTTPOk, json_response
from discord import Status

log.info("Handler /test defined")
@routes.post('/test')
async def message(request: Request):
    log.debug(await request.json())
    return HTTPOk(body="Success")

@routes.get('/server')
async def server(request: Request):
    """Renvoie les informations sur le serveur discord"""
    guild = client.get_guild(GUILD_ID)

    return json_response({
        "name": guild.name,
        "members": guild.member_count,
        "online": len([member for member in guild.members if member.status.value != "offline"])
    })