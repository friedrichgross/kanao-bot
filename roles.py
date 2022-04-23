import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import Cog
from discord.ext.commands import command
import logging

from discord.raw_models import RawReactionActionEvent

from reaction_roles import *

logger = logging.getLogger(__name__)


class Roles(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    """

    Check for missed reactions while offline

    """
    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f'{self.bot.user} has connected to Discord')
        if SERVER_ID is not None:
            logger.info("Checking if we missed any reaction roles while offline")
            await restore_reaction_roles(self.bot)
        else:
            logger.warning("No SERVER_ID set, skipping reaction role restoration")
        logger.info(f'{self.bot.user} has finished initialising')
        await self.bot.change_presence(activity=discord.Game(name="k!help"))


    """

    Reaction roles add

    """
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        _role = await get_role(self.bot, payload)
        if _role is not None:
            try:
                await payload.member.add_roles(_role)
                logger.info(f"Added role '{_role.name}' to user '{payload.member.name}'")
            except discord.HTTPException:
                logger.error("HTTPException")
                payload.channel.send("It appears the discord API is not available.\nPlease contact an admin if the problem persists.", delete_after=30)
                pass


    """

    Reaction roles remove

    """
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent):
        _role = await get_role(self.bot, payload)

        if _role is not None:
            try:
                _guild = bot.get_guild(payload.guild_id)
                _member = _guild.get_member(payload.user_id)
                if _member is None:
                    logger.error(f"Could not find user '{_member.name}'")
                    return

                await _member.remove_roles(_role)
                logger.info(f"Removed role '{_role.name}' from user '{_member.name}'")
            except discord.HTTPException:
                logger.error("HTTPException")
                payload.channel.send("It appears the discord API is not available.\n" +
                                     "Please contact an admin if the problem persists.", delete_after=30)

                pass

"""

Retrieves a role for a given reaction by looking up the emoji in the REACTION_ROLES_MAP list.
Also clears reaction-emojis that are not in the list from the message

"""
async def get_role(bot: Bot, payload):
    if payload.message_id in REACTION_ROLE_MSG_IDS.values():
        _guild = bot.get_guild(payload.guild_id)
        if _guild is None:
            logger.error("No guild/server??")
            return
        try:
            return discord.utils.get(_guild.roles, name=REACTION_ROLES_MAP[payload.emoji.name])
        except KeyError:
            print("Reaction roles: Role for Emoji '" + payload.emoji.name + "' not found, removing reaction.")
            _channel = bot.get_channel(payload.channel_id)
            logger.warning(f"User '{payload.member.name}' reacted with '{payload.emoji.name}' in channel '{_channel.name}', but no role was found for that emoji. Removing reaction")
            _msg = await _channel.fetch_message(payload.message_id)
            for _reaction in _msg.reactions:
                if str(_reaction.emoji) == str(payload.emoji):
                    await _reaction.clear()
                print("Reaction Roles: Cleared reaction")
                return
 
"""

Checks if all users who reacted to the selfroles-msg have the corresponding role & gives it to them if they don't.
Also clears all reactions that are not corresponding to a role.

"""
async def restore_reaction_roles(bot: Bot):
    for channel_id in REACTION_ROLE_MSG_IDS.keys():
        _channel = bot.get_channel(channel_id)
        if _channel is None:
            logger.error(f"Could not restore reaction roles: channel_id '{channel_id}' not found. Quitting")
            return

        try:
            _msg = await _channel.fetch_message(REACTION_ROLE_MSG_IDS[channel_id])
        except Exception as e:
            logger.error(f"Could not fetch channel: {e}")
            return

        _guild = bot.get_guild(int(SERVER_ID))
        for reaction in _msg.reactions:
            try:
                _role = discord.utils.get(_guild.roles, name=REACTION_ROLES_MAP[reaction.emoji])
            except KeyError:
                logger.warning(f"Role for Emoji '{reaction.emoji.name}' sent by user '{member.name}' in channel {_channel.name} not found, removing reaction")
                await reaction.clear()
                continue

            try:
                async for member in reaction.users():
                    # Skip admins bc we don't want to get EVERY role all the time
                    if member.name in REACTION_ROLE_RESTORE_IGNORED_MEMBERS:
                        continue

                    # Check if user already has the role:
                    try:
                       _role = discord.utils.get(_guild.roles, name=REACTION_ROLES_MAP[reaction.emoji])
                    except KeyError:
                        print(
                            "Reaction roles restore: Role for Emoji '" + reaction.emoji.name + "' not found, removing reaction.")
                        await reaction.clear()
                        print("Reaction roles restore: Cleared reaction")
                        continue
                    if not _role in member.roles:
                        logger.info(f"User '{member.name}' does not yet have the '{REACTION_ROLES_MAP[reaction.emoji]}' role, but has sent the reaction for it. Adding role now")
                        try:
                            await member.add_roles(_role)
                        except discord.HTTPException:
                            logger.error("HTTPException")
                            pass

            except discord.HTTPException:
                logger.error("HTTPException")


def setup(bot: Bot) -> None:
    bot.add_cog(Roles(bot))
