

from modules.pinet.classes import Wallet


wallet = Wallet("GC5NAVYCC7GYZO2LRTDJXJZFAWAGTKNHJBX43TN2RBMEOAUN37FMSEZD")
print((await wallet.get_testnet_history())[0])