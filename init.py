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
WALLET_PI_FULCRAN = "GCGH7QAXTHULPAWQOMTI26NY7BL36SUSVX6KTMZUSZLZD2XPIHFX6Z7J"
BADGE = Literal["Vérifié", "Vendeur de confiance"]

class SharedStorage:
    """shared read and write storage accross files"""

    __slots__ = ('bitcoin_price')

    def __init__(self):
        self.bitcoin_price: int = 0

storage = SharedStorage()

log.info(f"Strarting in {"🧪" if MODE == "DEV" else "🚀"} {MODE} mode...")
if MODE == "DEV":
    PORT = 18101
    GUILD_ID = TEST_GUILD_ID
    SIGNIN_TICKET_CATEGORY_ID = 1313419310106152970
    BUYER_ROLE_ID = 1310271143168573450
    SELLER_ROLE_ID = 1310271119466565755
    SHOP_CHANNEL_ID = 1317065482112733264
    SHOP_MESSAGE_ID = 1326908199286214667
    ADMIN_NOTIFICATIONS_CHANNEL_ID = 1313062267624886282
    SELL_POST_CHANNEL_ID = 1310526655101407232
    SIGNIN_CHANNEL_ID = 1310229664244961361
    SIGNIN_MESSAGE_ID = 1310229676383277121
    OPENNODE_CALLBACK_URL = "https://swakraft.hopto.org/api/opennode/{action}/test-bitbot"

else: # PROD
    PORT = 17101
    GUILD_ID = PROD_GUILD_ID
    SIGNIN_TICKET_CATEGORY_ID = 1315981531046613002
    BUYER_ROLE_ID = 1009099124597080115
    SELLER_ROLE_ID = 1009099480076931123
    SHOP_CHANNEL_ID = 1243147760467841045
    SHOP_MESSAGE_ID = 1338543457479950351
    ADMIN_NOTIFICATIONS_CHANNEL_ID = 1025464172185669732
    SELL_POST_CHANNEL_ID = 1305173523391840318
    SIGNIN_CHANNEL_ID = 1247211754283601931
    SIGNIN_MESSAGE_ID = 1247211829344866387
    OPENNODE_CALLBACK_URL = "https://swakraft.hopto.org/api/opennode/{action}/bitbot"