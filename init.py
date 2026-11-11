from chauff_cmn.logging import configure
from settings import settings

configure(service = "bitbot", level = settings.log_level)
from bot.interactions.util import InteractionHandler
from discord import Client, Intents, app_commands
from aiohttp import web
from dotenv import load_dotenv

load_dotenv('data/.env')
intents = Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
client = Client(intents = intents)
tree = app_commands.CommandTree(client)

app = web.Application()
routes = web.RouteTableDef()
interaction_handler = InteractionHandler()
