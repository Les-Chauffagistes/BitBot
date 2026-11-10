from discord import TextChannel, Member, CategoryChannel, Interaction
from settings import settings
from ..utils import create_ticket as make_ticket

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
            channel = await make_ticket(interaction.user, interaction.channel,"user")
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


    @interaction_handler.register_interaction("CLOSE_TICKET")
    async def close_ticket(interaction: Interaction, _):
        assert interaction.guild
        assert isinstance(interaction.user, Member)
        assert isinstance(interaction.channel, TextChannel)

        await interaction.channel.edit(sync_permissions = True)
        await interaction.response.send_message(
            "Le ticket a été fermé avec succès.",
            ephemeral = True
        )

    @interaction_handler.register_interaction("DELETE_TICKET")
    async def delete_ticket(interaction: Interaction, _):
        assert isinstance(interaction.channel, TextChannel)

        await interaction.response.edit_message()
        await interaction.channel.delete()
