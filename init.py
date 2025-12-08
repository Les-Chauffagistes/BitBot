print(open("name").read())

from typing import Literal, cast
from discord import Client, Intents, app_commands
from modules.logger import Logger
from aiohttp import web
from dotenv import load_dotenv
from os import getenv

log = Logger()

log.debug('Loading env variables...')
load_dotenv('data/.env')
intents = Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
client = Client(intents = intents)
tree = app_commands.CommandTree(client)
token = getenv('DISCORD_API_TOKEN')
assert token is not None
token = cast(str, token)

app = web.Application()
routes = web.RouteTableDef()

log.info("Defining constants")
PROD_GUILD_ID = 809374366592401419
TEST_GUILD_ID = 1306611983092682822
FULCRAN_ID = 276123659050024962
COLOR = 0xDE983D

SYNC = False
SERVER_NAME = "Pill Lab's"
MODE = getenv("MODE")
assert MODE in ["DEV", "PROD"]
MODE = cast(Literal["DEV", "PROD"], MODE)

class SharedStorage:
    """shared read and write storage accross files"""

    __slots__ = ('bitcoin_price', 'bitcoin_block_reward')

    def __init__(self):
        self.bitcoin_price: int = 0
        self.bitcoin_block_reward: float = 0.0

storage = SharedStorage()

log.info(f"Strarting in {"🧪" if MODE == "DEV" else "🚀"} {MODE} mode...")
if MODE == "DEV":
    PORT = 18101
    GUILD_ID = TEST_GUILD_ID
    ADMIN_NOTIFICATIONS_CHANNEL_ID = 1313062267624886282
    OPENNODE_CALLBACK_URL = "https://swakraft.fr/api/opennode/{action}/test-bitbot"

else: # PROD
    PORT = 17101
    GUILD_ID = PROD_GUILD_ID
    ADMIN_NOTIFICATIONS_CHANNEL_ID = 1025464172185669732
    OPENNODE_CALLBACK_URL = "https://swakraft.fr/api/opennode/{action}/bitbot"