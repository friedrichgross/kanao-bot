from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import Cog
import logging

from reaction_roles import *

logger = logging.getLogger(__name__)


class MessageEvents(Cog,
    description="Events, that relate to messages.",
):

    def __init__(self, bot: Bot):
        self.bot = bot

    """

    check if a message tries to role mention without using k!pingRole
    advise user if that's the case
    Extensible for further message checks

    """
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        _ctx = await self.bot.get_context(message)
        if _ctx.valid:
            return
        if _ctx.message.raw_role_mentions:
            if not _ctx.author.guild_permissions.mention_everyone:
                logger.warning(f"User {_ctx.author.name} tried to use raw role mentions without permissions in channel '{_ctx.channel.name}'")
                await message.channel.send("Normal users need to use the k!pingRole command to mention a role!", reference=message)

    """
    log message edits
    will not be called if the message isn't in the msg cache (anymore). 
    the msg cache, by default is 5k, which i deem enough.
    otherwise, on_raw_message_edit is recommended, or raising Client.max_messages

    """
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return
        _editLogChannel = self.bot.get_channel(MESSAGE_EDIT_LOG)
        print(_editLogChannel)
        await _editLogChannel.send("```EDIT EVENT:\n\n" + "User: " + before.author.name + "\n\n" +
                            "Before: " + before.content + "\n\n" +
                            "After: " + after.content + "```")

    """ 

    message delete event
    same things as with on_message_edit apply

    """
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        _editLogChannel = self.bot.get_channel(MESSAGE_EDIT_LOG)
        await _editLogChannel.send("```MSG DELETE EVENT:\n\n" + "User: " + message.author.name + "\n\n" +
                            "Channel: " + message.channel.name + "\n"
                            "Message: " + message.content + "```")

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, payload):
        _modLogChannel = self.bot.get_channel(MOD_LOG)
        _eventChannel = self.bot.get_channel(payload.channel_id)
        try:
            await _modLogChannel.send("```!! BULK DELETE EVENT !!" + "\n\n" + "Channel :" + _eventChannel.name + "\n\n"
                                     "Trying to get possibly cached messages: ```")
            for _msg in payload.cached_messages:
                await _modLogChannel.send("```" + _msg.author.name + ":\n" + _msg.content + "\n" + "```")

        except:
            await _modLogChannel.send("Failed getting any cached messages.")

def setup(bot: Bot):
    bot.add_cog(MessageEvents(bot))

