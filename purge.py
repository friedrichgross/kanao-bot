from discord.ext import commands
from discord.ext.commands import Bot
import logging
from reaction_roles import MOD_ROLES

logger = logging.getLogger(__name__)

"""

allows purging of up to 100 messages. only mods and admins.
factors in the commanding messages automatically 

"""


@commands.command()
@commands.has_any_role(MOD_ROLES)
async def purge(ctx, arg):
    _to_delete = int(arg) + 1
    _delete_list = []
    async for message in ctx.history(limit=_to_delete):
        _delete_list.append(message)
    logger.info(f"Purging {_to_delete} messages for user '{ctx.author.name}' in channel '{ctx.channel.name}'")
    await ctx.channel.delete_messages(_delete_list)


@purge.error
async def purge_error(ctx, error):
    logger.error(f"Purge Error for user '{ctx.author.name}' in channel '{ctx.channel.name}': {error}")
    if isinstance(error, commands.MissingAnyRole):
        await ctx.send("No perms? 🤨", delete_after=10, reference=ctx.message)


def setup(bot: Bot):
    bot.add_command(purge)
