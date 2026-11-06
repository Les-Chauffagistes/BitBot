from discord import TextChannel
from discord import Member
from discord import PermissionOverwrite
from discord import CategoryChannel, Interaction
from settings import settings

from init import interaction_handler


def register_ticket_interactions():
    @interaction_handler.register_interaction("CREATE_TICKET")
    async def create_ticket(interaction: Interaction, _):
        assert interaction.guild
        assert isinstance(interaction.user, Member)

        channel = interaction.guild.get_channel(settings.support_category_id)
        if not isinstance(channel, CategoryChannel):
            await interaction.response.send_message(
                "Impossible de créer un ticket à cause d'une erreur technique. Contactez directement un administrateur.",
                ephemeral = True
            )
            return

        try:
            channel = await channel.create_text_channel(
                name = interaction.user.name,
                reason = f"Ticket créé par {interaction.user.name} via le bot",
                overwrites = {
                    interaction.guild.default_role: PermissionOverwrite(read_messages = False),
                    interaction.user: PermissionOverwrite(read_messages = True)
                }
            )
        except:
            await interaction.response.send_message(
                "Impossible de créer un ticket à cause d'une erreur technique. Contactez directement un administrateur.",
                ephemeral = True
            )
            return
        await interaction.response.send_message(
            f"Ticket créé avec succès ! Vous pouvez le retrouver ici : {channel.mention}",
            ephemeral = True
        )
        try:
            await channel.send(
                f"Bonjour {interaction.user.mention}, un membre de l'équipe va vous répondre dès que possible. "
                "En attendant, merci de décrire votre problème en détail et d'ajouter toute information pertinente."
            )
        except:
            pass

    @interaction_handler.register_interaction("CLOSE_TICKET")
    async def close_ticket(interaction: Interaction, _):
        assert interaction.guild
        assert isinstance(interaction.user, Member)
        assert isinstance(interaction.channel, TextChannel)

        await interaction.channel.edit(sync_permissions=True)
        await interaction.response.send_message(
            "Le ticket a été fermé avec succès.",
            ephemeral = True
        )

    @interaction_handler.register_interaction("DELETE_TICKET")
    async def delete_ticket(interaction: Interaction, _):
        assert isinstance(interaction.channel, TextChannel)

        await interaction.response.edit_message()
        await interaction.channel.delete()