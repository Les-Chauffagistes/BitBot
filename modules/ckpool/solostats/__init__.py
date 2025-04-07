from . import api
from . import classes
from .classes import Miner

async def get_miners(): return await Miner.get_miner_info()