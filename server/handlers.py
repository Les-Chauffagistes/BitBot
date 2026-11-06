from init import routes, client
from aiohttp.web_request import Request
from aiohttp.web import json_response


@routes.get('/health')
async def health(_: Request):
    return json_response({"status": client.is_ready() and client.user is not None})
