from init import COLOR, GUILD_ID, routes, log, client
from aiohttp.web_request import Request
from aiohttp.web import HTTPOk

@routes.post('/test')
async def message(request: Request):
    log.debug(await request.json())
    return HTTPOk(body="Success")