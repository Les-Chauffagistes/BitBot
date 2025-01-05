from typing import Literal
from discord import Client, Intents, app_commands
from modules.logger import Logger
from aiohttp import web
from dotenv import load_dotenv
from os import getenv

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

log.info("Defining constants")
PROD_GUILD_ID = 809374366592401419
TEST_GUILD_ID = 1306611983092682822
FULCRAN_ID = 276123659050024962
COLOR = 0x0
PORT = None
SYNC = False
SERVER_NAME = "Pill Lab's"
MODE: Literal["DEV", "PROD"] = getenv("MODE")
WALLET_PI_FULCRAN = "GCGH7QAXTHULPAWQOMTI26NY7BL36SUSVX6KTMZUSZLZD2XPIHFX6Z7J"

log.info(f"Strarting in {"🧪" if MODE == "DEV" else "🚀"} {MODE} mode...")
if MODE == "DEV":
    GUILD_ID = TEST_GUILD_ID
    SIGNIN_TICKET_CATEGORY_ID = 1313419310106152970
    BUYER_ROLE_ID = 1310271143168573450
    SELLER_ROLE_ID = 1310271119466565755
    SHOP_CATEGORY = 1317062699552608266
    ADMIN_NOTIFICATIONS_CHANNEL_ID = 1313062267624886282
    SELL_POST_CHANNEL_ID = 1310526655101407232

else:
    GUILD_ID = PROD_GUILD_ID
    SIGNIN_TICKET_CATEGORY_ID = 1315981531046613002
    BUYER_ROLE_ID = 1009099124597080115
    SELLER_ROLE_ID = 1009099480076931123
    SHOP_CATEGORY = 1239300373794127902
    ADMIN_NOTIFICATIONS_CHANNEL_ID = 1025464172185669732
    SELL_POST_CHANNEL_ID = 1305173523391840318
