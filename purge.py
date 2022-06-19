import logging
import discord

logger = logging.getLogger(__name__)

"""

allows purging of up to 100 messages. only mods and admins.
factors in the commanding messages automatically 

"""
@discord.app_commands.command(name="purge", description="Purges an amount of messages from the channel")
@discord.app_commands.describe(amount="How many messages should be deleted")
@discord.app_commands.checks.has_any_role("Moderator", "Admin")
async def purge(interaction, amount: int):
    _delete_list = [message async for message in interaction.channel.history(limit=amount)]
    # async for message in interaction.channel.history(limit=_to_delete):
    #     _delete_list.append(message)
    logger.info(f"Purging {amount} messages for user '{interaction.user.name}' in channel '{interaction.channel.name}'")
    try:
        await interaction.channel.delete_messages(_delete_list)
        await interaction.response.send_message(f"Successfully deleted {amount} messages.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Could not delete {amount} messages: {e}", ephemeral=True)
    

@purge.error
async def purge_error(interaction, error):
    logger.error(f"Purge Error for user '{interaction.user.name}' in channel '{interaction.channel.name}': {error}")
    if isinstance(error, discord.app_commands.MissingAnyRole):
        await interaction.response.send_message("No perms? 🤨", ephemeral=True)


def setup(bot, cmd_tree):
    cmd_tree.add_command(purge)
