import traceback
from typing import Literal, Optional
from discord import ButtonStyle, Embed, Interaction, TextStyle, User
from discord.app_commands import Group, describe, Range
from discord.ui import View, Button, Modal, TextInput
from classes.commands import Command
from classes.discord_wallet import PiWallet
from classes.emoji import Emoji
from init import COLOR, log
from views.pi_wallet import wallet_view

class CustomGroup(Group):
    pass

pi = CustomGroup(name = "pi", description = "Intégration Pi Network")

@pi.command(
    name = "wallet",
    description = "Affiche votre wallet Pi Network"
)
@describe(network = "Réseau sur lequel chercher votre wallet Pi")
async def wallet(interaction: Interaction, network: Literal['Mainnet', 'Testnet', 'Discord'], utilisateur: Optional[User]):
    try:
        match network:
            case "Discord":
                wallet = await PiWallet.from_user(utilisateur.id if utilisateur else interaction.user.id)
                if wallet:
                    embed, file = await wallet_view(wallet, network)
                    await interaction.response.send_message(
                        embed = embed,
                        file = file
                    )

                else:
                    embed = Embed(
                        title = "Aucun wallet sur le réseau",
                        description = f"Vous n'avez aucun wallet Pi Network sur le réseau {network}",
                        color = COLOR
                    )
                    view = View(timeout = None)
                    if not utilisateur:
                        view.add_item(
                            Button(
                                label = "Créer mon wallet",
                                style = ButtonStyle.primary,
                                emoji = Emoji.wallet.value,
                                custom_id = f"CREATEDCWALLET#{interaction.user.id}"
                            )
                        )

                    await interaction.response.send_message(
                        embed = embed,
                        view = view
                    )
            
            case "Mainnet" | "Testnet":
                wallet = await PiWallet.from_user(utilisateur.id if utilisateur else interaction.user.id)
                if wallet.address:
                    embed, file = await wallet_view(wallet, network)
                    await interaction.response.send_message(
                        embed = embed,
                        file = file
                    )
                
                else:
                    if not utilisateur:
                        await interaction.response.send_message(
                            embed = Embed(
                                title = "Adresse non connue",
                                description = f"Vous devez saisir votre adresse Pi Network pour que BitBot puisse récupérer votre solde à partir de la blockchain. Utilisez la commande {Command.pi_profile_edit}.",
                                color = COLOR
                            )
                        )
                    
                    else:
                        await interaction.response.send_message(
                            embed = Embed(
                                title = "Adresse non connue",
                                description = f"{utilisateur.display_name} n'a pas fourni son adresse Pi Network.",
                                color = COLOR
                            )
                        )

    
    except:
        log.warn(traceback.format_exc())

@pi.command(
    name = "send",
    description = "Envoyer des Pi via le Discord"
)
@describe(montant = "Montant à envoyer", membre = "Membre à qui envoyer", message = "Message facultatif à joindre")
async def sendCommand(interaction: Interaction, montant: Range[int, 1, 10_000], membre: User, message: Optional[str]):
    try:
        sender_wallet = await PiWallet.from_user(interaction.user.id)
        if sender_wallet:
            try:
                recipient_wallet = await PiWallet.from_user(membre.id)
                if not recipient_wallet:
                    recipient_wallet = await PiWallet.create_new(membre)
                
                await sender_wallet.send(montant, recipient_wallet)
            
            except ValueError:
                await interaction.response.send_message(
                    embed = Embed(
                        title = "Montant invalide",
                        description = "Veuillez saisir un montant valide",
                        color = COLOR
                    ),
                    ephemeral = True
                )
                return

            except PiWallet.FundsError:
                await interaction.response.send_message(
                    embed = Embed(
                        title = "Fonds insuffisants",
                        description = f"Vous n'avez pas assez de Pi pour envoyer {montant} Pi à {membre.display_name}",
                        color = COLOR
                    ),
                    ephemeral = True
                )
                return
        
            except:
                log.warn(traceback.format_exc())
                await interaction.response.send_message(
                    embed = Embed(
                        title = "Échec de la transaction",
                        description = f"La transaction a échoué. Réessayez plus tard",
                        color = COLOR
                    ),
                    ephemeral = True
                )
                return

            

            try:
                await membre.send(
                    embed = Embed(
                        title = "Vous avez reçu du Pi",
                        description = f"{interaction.user.display_name} vous a envoyé {montant} Pi sur votre wallet Discord",
                        color = COLOR
                    )
                )
                success = True
            
            except:
                success = False
            
            await interaction.response.send_message(
                embed = Embed(
                    title = "Pi envoyé",
                    description = f"Vous avez envoyé {montant} Pi à {membre.display_name}. {f"La notification n'a pas pu être envoyée via MP, car {membre.display_name} n'accepte pas les MP du bot." if not success else ''}",
                    color = COLOR
                )
            )

        
        else:
            await interaction.response.send_message(
                embed = Embed(
                    title = "Votre wallet est vide",
                    description = "Déposez des fonds sur Discord, puis réessayez",
                    color = COLOR
                ),
                ephemeral = True
            )
    
    except:
        log.warn(traceback.format_exc())

@pi.command(
    name = "deposit",
    description = "Déposer des pis sur Discord"
)
async def depositCommand(interaction: Interaction, montant: Range[int, 1, 10_000]):
    try:
        user_wallet = await PiWallet.from_user(interaction.user.id)
        if not user_wallet:
            user_wallet = await PiWallet.create_new(interaction.user)
        
        embed = await user_wallet.start_deposit(montant)

        await interaction.response.send_message(
            embed = embed,
            ephemeral = True
        )

    except:
        log.warn(traceback.format_exc())

@pi.command(
    name = "withdraw",
    description = "Retirer des Pi sur Discord"
)
async def withdrawCommand(interaction: Interaction, montant: Range[int, 1, 10_000]):
    try:
        user_wallet = await PiWallet.from_user(interaction.user.id)
        if not user_wallet:
            await interaction.response.send_message(
                embed = Embed(
                    title = "Retrait impossible",
                    description = "Un wallet avec des fonds est requis pour retirer des π",
                    color = COLOR
                ),
                ephemeral = True
            )
        
        else:
    
            try:
                await user_wallet.start_withdrawal(montant)
                await interaction.response.send_message(
                    embed = Embed(
                        title = "Votre demande de retrait a été soumise",
                        description = f"Les retraits sont traités manuellement, vous recevrez un message lorsque votre retrait sera traité. Les fonds seront déplacés vers votre wallet ```{user_wallet.address}```",
                        color = COLOR
                    )
                )
            
            except:
                await interaction.response.send_message(
                    embed = Embed(
                        title = "Fonds insuffisants",
                        description = f"Votre solde est de {round(user_wallet.balance)} π, vous ne pouvez pas retirer {montant} π",
                        color = COLOR
                    ),
                    ephemeral = True
                )

    except:
        log.warn(traceback.format_exc())