from discord.ext.commands import Bot
from discord.ext import commands
from discord import Member
from reaction_roles import *
import logging

logger = logging.getLogger(__name__)
_defaultreason = "No Reason has been given"
"""
Use k!kick @user reason to kick someone using kanao
"""
@commands.command()
@commands.has_permissions(kick_members = True)
async def kick(ctx,member:Member,*,_reason = None):
    if (_reason == None):
        _reason = _defaultreason
#if channel isn't provided, kanao will not be able to kick/ban
    _editLogChannel = ctx.bot.get_channel(MOD_LOG)
    logger.info(f'User {ctx.author.name} Kicked : {member}.')
    await _editLogChannel.send(f'user {ctx.author.name} has kicked user {member}')
    #reason has to be supplied with reason = _reason, due to the function not working otherwise
    #same with ban
    await member.kick(reason = _reason)
    await ctx.send(f'{member} has been kicked')

@kick.error
async def kick_error(ctx,error):
    logger.error(f'Kick error for User: {ctx.author.name}, who tried to kick {ctx}')
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("No Perms? ", delete_after = 10, refernce=ctx.message)
"""
Use k!ban @user reason to ban someone using kanao
"""

@commands.command()
@commands.has_permissions(ban_members = True)
async def ban(ctx,member:Member,*,_reason = None):
    if(_reason == None):
        _reason = _defaultreason
    _editLogChannel = ctx.bot.get_channel(MOD_LOG)
    logger.info(f'user {ctx.author.name} has banned user {member}')
    await _editLogChannel.send(f'user {ctx.author.name} has banned user {member}')
    await member.ban(reason = _reason)
    await ctx.send(f'{member} has been banned')

@ban.error
async def ban_error(ctx,error):
    logger.error(f"Ban Error for user '{ctx.author.name}' While trying to ban:'{Member}': {error}")
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("No perms? 🤨", delete_after=10, reference=ctx.message)

"""
@commands.command()
@commands.has_permissions(ban_members = True)
async def unban(ctx,_user:str,reason = None):
    _editLogChannel = ctx.bot.get_channel(channel_id)
    await _editLogChannel.send(f'user {ctx.author.name} has unbanned {Member}.')   
    #need to use the guild function due to the user not being snowlake(sharing a server)
    #stripping the signs so we can cast on an int, which represents the ID
    _user = _user.strip("<")
    _user = _user.strip(">")
    _user = _user.strip("@")
    _user = int(_user)
    _banneduser =  await ctx.bot.fetch_user(_user)
    #need to look into how to use this unban function.
    await Member.unban(_banneduser)
"""

def setup(bot: Bot):
    bot.add_command(kick)
    bot.add_command(ban)
    #bot.add_command(unban)