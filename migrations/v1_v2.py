from json import dumps, loads
import os
from aiofiles import open

fulcran_path = "../../Fulcran"
fulcran_data_path = f"{fulcran_path}/data"
bitbot_data_path = "data"

print("hello, ", os.getcwd())

async def fromV1toV2():
    # state: Ready to use
    async with open(os.path.abspath(f"{fulcran_data_path}/pis.json")) as pis_file:
        pis_data: dict[str, int] = loads(await pis_file.read())

    async with open(os.path.abspath(f"{fulcran_data_path}/business/profils.json")) as file:
        profiles_data: list[dict[str, bool | str | int]] = loads(await file.read())
        for profile in profiles_data:
            async with open(os.path.abspath(f"../{bitbot_data_path}/wallets/pi/{profile['user_id']}.json"), 'w') as new_file:
                contents: dict[str, str | None | list[str] | list[int] | bool] = {
                    "id": profile['user_id'],
                    "badges": [],
                    "balance": pis_data.get(str(profile['user_id']), 0),
                    "validation_amount": None,
                    "payments_ids": [],
                    "address": profile['key'],
                    "locale": profile['local'],
                    "reason": 'deposit'
                }

                if profile["verified"]:
                    contents["badges"].append('verified')
                
                await new_file.write(dumps(contents, indent = 4))