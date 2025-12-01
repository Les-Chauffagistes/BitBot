import pytest
from classes.discord_wallet import BitcoinWallet
from classes.discord_wallet import BaseDiscordWallet


def test_creation():  # Reste une fonction synchrone
    wallet = BitcoinWallet(1234, 0)
    assert wallet.balance == 0
    assert wallet.id == 1234


@pytest.mark.asyncio
async def test_transfert_classic():  # Doit être async car on attend une coroutine
    wallet1 = BitcoinWallet(1234, 30)
    wallet2 = BitcoinWallet(5678, 30)

    await wallet1.send(10, wallet2)  # Supposons que send() est une coroutine

    assert wallet1.balance == 20
    assert wallet2.balance == 40

    await wallet1.save()
    await wallet2.save()

    wallet1_restored = await BitcoinWallet.from_user_id(1234)
    wallet2_restored = await BitcoinWallet.from_user_id(5678)

    assert wallet1.balance == wallet1_restored.balance
    assert wallet2.balance == wallet2_restored.balance


@pytest.mark.asyncio
async def test__transfer():
    wallet1 = BitcoinWallet(1234, 30)
    wallet1_bis = wallet1

    await wallet1.send(10, wallet1_bis)
    assert wallet1.balance == 30
    assert wallet1_bis.balance == 30

    await wallet1_bis.save()
    wallet1_restored = await BitcoinWallet.from_user_id(1234)

    assert wallet1.balance == wallet1_restored.balance
    assert wallet1.balance == wallet1_bis.balance


@pytest.mark.asyncio
async def test_transfer_invalid_amount():
    wallet1 = BitcoinWallet(1234, 30)
    wallet2 = BitcoinWallet(5678, 30)

    try:
        await wallet1.send(-10, wallet2)
        assert False

    except AssertionError:
        pass


@pytest.mark.asyncio
async def test_transfer_with_invalid_funds():
    wallet1 = BitcoinWallet(1234, 30)
    wallet2 = BitcoinWallet(5678, 30)

    try:
        await wallet1.send(40, wallet2)
        assert False

    except BaseDiscordWallet.FundsError:
        pass


@pytest.mark.asyncio
async def test_new_wallet():
    new_wallet = await BitcoinWallet.from_user_id(1010)
    assert new_wallet.balance == 0
    assert new_wallet.id == 1010


@pytest.mark.asyncio
async def test_load_twice_wallet():
    wallet_a = await BitcoinWallet.from_user_id(1234)
    wallet_b = await BitcoinWallet.from_user_id(1234)

    await wallet_a.send(10, wallet_b)
    assert wallet_a.balance == wallet_b.balance