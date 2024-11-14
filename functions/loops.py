import traceback
from init import client, log
from asyncio import sleep, CancelledError
from datetime import datetime, timedelta

async def loop():
    log.info("En ligne")
    while True:
        try: # Loop instructions
            pass

        except CancelledError: # Task cancelled (stopping bot)
            break

        except: # Unknown error
            log.warn(traceback.format_exc())
        
        finally:
            await sleep(7)