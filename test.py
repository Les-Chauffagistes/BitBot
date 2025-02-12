from modules import ckpool

miners = await ckpool.get_miners()
miner1 = miners[0]
print(await miner1.shares)