from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import Cog
import logging

logger = logging.getLogger(__name__)


class Purge(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    """

    allows purging of up to 100 messages. only mods and admins.
    factors in the commanding messages automatically 

    """
    @commands.command()
    @commands.has_any_role("Moderator", "Admin")
    async def purge(self, ctx, arg):
        try:
            _to_delete = int(arg) + 1
        except ValueError:
            logger.warning(f"Purge error: Could not convert '{arg}' into an integer...")
            await ctx.send(f"I tried, but I couldn't convert `{arg}` into an integer... 😭", delete_after=10)
            return
        _delete_list = []
        async for message in ctx.history(limit=_to_delete):
            _delete_list.append(message)
        logger.info(f"Purging {_to_delete} messages for user '{ctx.author.name}' in channel '{ctx.channel.name}'")
        await ctx.channel.delete_messages(_delete_list)


    @purge.error
    async def purge_error(self, ctx, error):
        logger.error(f"Purge Error for user '{ctx.author.name}' in channel '{ctx.channel.name}': {error}")
        if isinstance(error, commands.MissingAnyRole):
            await ctx.send("No perms? 🤨", delete_after=10, reference=ctx.message)


def setup(bot: Bot):
    bot.add_cog(Purge(bot))
