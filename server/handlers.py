from json import loads
import traceback
from typing import Literal, cast
from classes.discord_wallet import BitcoinWallet
from classes.emoji import Emoji
from functions.utils import send_admin
from init import COLOR, GUILD_ID, MODE, routes, log, client
from aiohttp.web_request import Request
from aiohttp.web import HTTPOk, json_response
from discord import Embed, Guild, Member
from aiohttp import web
from modules.opennode.model.webhooks.withdraw import Withdraw, lnurl

log.debug("Creating handlers...")


@routes.get('/test')
async def message(request: Request):
    log.debug("OK")
    return HTTPOk(body="Success")

@routes.get('/server')
async def server(request: Request):
    """Renvoie les informations sur le serveur discord"""
    guild = cast(Guild, client.get_guild(GUILD_ID))

    return json_response({
        "name": guild.name,
        "members": guild.member_count,
        "online": len([member for member in guild.members if member.status.value != "offline"])
    })

log.info("Handler /deposit/pay defined")
@routes.post('/bitcoin/pay')
async def bitcoin_deposit(request: Request):
    try:
        log.debug("/deposit")
        payload: dict = await request.json()
        user_id: int = payload.get('order_id', 0)
        guild = client.get_guild(GUILD_ID)
        assert guild
        member = guild.get_member(user_id)
        sats = int(payload['price'])
        fees = int(payload['fee'])
        status = cast(Literal['processing', 'paid', 'expired', 'underpaid', 'processing'], payload.get('status', 'unpaid'))
        if status == "expired":
            return json_response({"status": "ok"})
    
        if status != "paid":
            log.warn(f"UNHANDLED ONCHAIN PAYMENT: {status}")
            log.debug(payload)
            return json_response({"status": "not supported"})
        
        log.info(f"{user_id} a déposé {sats} sats")

        wallet = await BitcoinWallet.from_user_id(user_id)
        await wallet.add_sat(sats - fees)
        if not member:
            user = client.get_user(user_id)
            if member:
                member = user
        
        if member:
            try:
                await member.send(
                    embed = Embed(
                        title = "Confirmation de dépot",
                        description = f"Vous avez déposé **{sats - fees}** {Emoji.sat} sur votre wallet Discord.",
                        color = COLOR,
                    ).set_image(
                        url = "https://swakraft.hopto.org/assets/bitcoin_wallet1"
                    )
                )
            
            except:
                log.warn(f'Unable to DM {member.id}')

        await send_admin(
            "Dépot de Sats",
            f"Dépot de **{sats - fees}** Sats sur son wallet Discord",
            member if isinstance(member, Member) else None
        )
        
        log.debug("Success")
        return web.Response()

    except:
        log.warn(traceback.print_exc())
        return web.Response()

log.info("Handler /bitcoin/withdraw defined")
@routes.post('/bitcoin/withdraw')
async def bitcoin_withdrawal(request: Request):
    log.debug("/withdraw")
    payload: Withdraw = await request.json()
    lnurl_payload: lnurl = loads(payload["lnurl_withdrawal"])
    log.debug(payload)
    user = client.get_user(int(lnurl_payload["id"]))
    if user:
        try:
            await user.send(
                embed = Embed(
                    title = "Confirmation de retrait",
                    description = f"Vous avez retiré **{payload['amount']}** {Emoji.sat} de votre wallet Discord.",
                    color = COLOR,
                ).set_image(
                    url = "https://swakraft.fr/assets/bitcoin_wallet1"
                )
            )
        
        except:
            log.warn(f'Unable to DM {user.id}')
    

    await send_admin(
        "Retrait de Sats",
        f"Retrait de **{payload['amount']}** Sats sur son wallet Discord",
        user
    )
    return web.Response()

@routes.post("/ispoolmember")
async def checkpoolmember(request: Request):
    data = await request.json()
    user_id = int(data["user_id"])
    guild = client.get_guild(GUILD_ID)
    assert guild
    member = guild.get_member(user_id)
    if MODE == "PROD":
        role = guild.get_role(1285186541185925131)
    
    else:
        role = guild.get_role(1356186777307840582)

    if member and role:
        if role in member.roles:
            return json_response({"is_pool_member": True})

    return json_response({"is_pool_member": False})

@routes.get('/user')
async def user(request: Request):
    user_id = request.query.get('user_id')
    if not user_id:
        return json_response({"status": "error", "error": "Missing user_id"}, status=400)
    
    guild = client.get_guild(GUILD_ID)
    assert guild
    member = guild.get_member(int(user_id))
    if member:
        url = member.display_avatar.url
        pseudo = member.display_name
        return json_response({"url": url, "pseudo": pseudo})

    else:
        return json_response(data={"status": "error", "error": "Member not found"}, status=404)