from discord.ext.commands import Bot
from discord.ext import commands
from discord import Member
from reaction_roles import *
import logging
#Hallo




logger = logging.getLogger(__name__)
defaultreason = "No Reason has been given" 

@commands.command()
@commands.has_permissions(kick_members = True)
async def kick(ctx,member:Member,*,reason = None):
    if (reason == None):
        reason = defaultreason
    _editLogChannel = ctx.bot.get_channel(MOD_LOG)
    await _editLogChannel.send(f'user {ctx.author.name} has kicked user {member}')
    await member.kick(reason = reason)
    await ctx.send(f'{member} has been kicked')

@kick.error
async def kick_error(ctx,error):
    logger.error(f'Kick error for User: {ctx.author.name}, who tried to kick {Member}')
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("No Perms? ", delete_after = 10, refernce=ctx.message)

@commands.command()
@commands.has_permissions(ban_members = True)
async def ban(ctx,member:Member,*,reason):
    if(reason == None):
        reason = defaultreason
    _editLogChannel = ctx.bot.get_channel(MOD_LOG)
    await _editLogChannel.send(f'user {ctx.author.name} has banned user {member}')
    await member.ban(reason = reason)
    await ctx.send(f'{member} has been banned')

@ban.error
async def ban_error(ctx,error):
    logger.error(f"Ban Error for user '{ctx.author.name}' While trying to ban:'{Member}': {error}")
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("No perms? 🤨", delete_after=10, reference=ctx.message)



def setup(bot: Bot):
    bot.add_command(kick)
    bot.add_command(ban)