import unittest
import unittest.async_case
from modules.ckpool import eusolo
from modules.ckpool.eusolo.model.pool import Pool


class TestPool(unittest.IsolatedAsyncioTestCase):
    async def test_get_user(self):
        user = await eusolo.get_user("bc1qh8ge36h2njrp2aqv5ddpyph4g22elzgkds52ae")
        self.assertEqual(isinstance(user, Pool), True) 

if __name__ == '__main__':
    unittest.main()