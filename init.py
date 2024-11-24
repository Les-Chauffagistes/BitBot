from typing import Literal
from discord import Client, Intents, app_commands
from modules.logger import Logger
from aiohttp import web
from dotenv import load_dotenv
from os import getenv
from classes import *

load_dotenv('data/.env')
intents = Intents.default()
intents.message_content = True
intents.members = True
intents.presences = False
client = Client(intents = intents)
tree = app_commands.CommandTree(client)
token = getenv('DISCORD_API_TOKEN')
log = Logger()
app = web.Application()
routes = web.RouteTableDef()

GUILD_ID = 0
COLOR = 0x0
PORT = None
SYNC = False
SERVER_NAME = "Pi Lab's"
MODE: Literal["DEV", "PROD"] = getenv("MODE")
WALLET_PI_FULCRAN = "GCGH7QAXTHULPAWQOMTI26NY7BL36SUSVX6KTMZUSZLZD2XPIHFX6Z7J"