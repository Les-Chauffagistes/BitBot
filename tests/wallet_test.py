import unittest
from classes.discord_wallet import BitcoinWallet
from commands.pi import wallet

class TestBitcoinWallet(unittest.IsolatedAsyncioTestCase):

    def test_creation(self):  # Reste une fonction synchrone
        wallet = BitcoinWallet(1234, 0)
        self.assertEqual(wallet.balance, 0)
        self.assertEqual(wallet.id, 1234)
    
    async def test_transfert_classic(self):  # Doit être async car on attend une coroutine
        wallet1 = BitcoinWallet(1234, 30)
        wallet2 = BitcoinWallet(5678, 30)

        await wallet1.send(10, wallet2)  # Supposons que send() est une coroutine

        self.assertEqual(wallet1.balance, 20)
        self.assertEqual(wallet2.balance, 40)

        await wallet1.save()
        await wallet2.save()

        wallet1_restored = await BitcoinWallet.from_user_id(1234)
        wallet2_restored = await BitcoinWallet.from_user_id(5678)

        self.assertEqual(wallet1.balance, wallet1_restored.balance)
        self.assertEqual(wallet2.balance, wallet2_restored.balance)

    async def test_self_transfer(self):
        wallet1 = BitcoinWallet(1234, 30)
        wallet1_bis = wallet1

        await wallet1.send(10, wallet1_bis)
        self.assertEqual(wallet1.balance, 30)
        self.assertEqual(wallet1_bis.balance, 30)

        await wallet1_bis.save()
        wallet1_restored = await BitcoinWallet.from_user_id(1234)

        self.assertEqual(wallet1.balance, wallet1_restored.balance)
        self.assertEqual(wallet1.balance, wallet1_bis.balance)
    
    async def test_transfer_invalid_amount(self):
        wallet1 = BitcoinWallet(1234, 30)
        wallet2 = BitcoinWallet(5678, 30)

        with self.assertRaises(AssertionError):
            await wallet1.send(-10, wallet2)
        
    async def test_transfer_with_invalid_funds(self):
        wallet1 = BitcoinWallet(1234, 30)
        wallet2 = BitcoinWallet(5678, 30)

        with self.assertRaises(BitcoinWallet.FundsError):
            await wallet1.send(40, wallet2)
    
    async def test_new_wallet(self):
        new_wallet = await BitcoinWallet.from_user_id(1010)
        self.assertEqual(new_wallet.balance, 0)
        self.assertEqual(new_wallet.id, 1010)
    
    async def test_load_twice_wallet(self):
        wallet_a = await BitcoinWallet.from_user_id(1234)
        wallet_b = await BitcoinWallet.from_user_id(1234)

        await wallet_a.send(10, wallet_b)
        self.assertEqual(wallet_a.balance, wallet_b.balance)

if __name__ == '__main__':
    unittest.main()