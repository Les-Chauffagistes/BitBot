from typing import Literal
from discord import CategoryChannel, Member, PermissionOverwrite

messages = {
    "user": "Bonjour {%s}, un membre de l'équipe va vous répondre dès que possible. "
            "En attendant, merci de décrire votre problème en détail et d'ajouter toute information pertinente.",
    "admin": "Bonjour {%s}, {%s} a ouvert ce ticket pour vous."
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
            messages[opened_by].format(for_member.mention, admin_member.mention if admin_member else None),
        )
    except:
        pass
    return ticket
