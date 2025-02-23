import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from modules.opennode import api

#charge = await api.create_charge(10, description = "test", order_id="1088153914823684208", callback_url=f"https://swakraft.hopto.org/api/opennode/pay/bitbot")
#charge.payreq

# await api.initiate_lnurl_withdrawal(min_amount = 10, max_amount = 100, callback_url = "https://swakraft.hopto.org/api/opennode/pay/test-bitbot", external_id = "1088153914823684208", description = "Retirer en tant que Hugo")