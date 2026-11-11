from typing import Literal
from discord import CategoryChannel, Member, PermissionOverwrite, TextChannel
from discord.abc import GuildChannel

from settings import settings

messages = {
    "user": "Bonjour {member}, un membre de l'équipe va vous répondre dès que possible. "
            "En attendant, merci de décrire votre problème en détail et d'ajouter toute information pertinente.",
    "admin": "Bonjour {member}, {admin} a ouvert ce ticket pour vous."
}


async def create_ticket(for_member: Member, category_support: CategoryChannel, opened_by: Literal["user", "admin"],
                        admin_member: Member | None = None):
    ticket = await category_support.create_text_channel(
        name = for_member.name,
        reason = f"Ticket créé par {for_member.name} via le bot",
        overwrites = {
            for_member.guild.default_role: PermissionOverwrite(read_messages = False),
            for_member: PermissionOverwrite(read_messages = True)
        }
    )
    try:
        await ticket.send(
            messages[opened_by].format(
                member = for_member.mention,
                admin = admin_member.mention if admin_member else None,
            ),
        )
    except Exception as e:
        pass
    return ticket


def is_ticket(channel: GuildChannel):
    from chauff_cmn.logging import logger as log
    log.debug(isinstance(channel, GuildChannel))
    log.debug(channel.category_id == settings.support_category_id)
    return isinstance(channel, TextChannel) and channel.category_id == settings.support_category_id
