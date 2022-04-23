from discord.ext.commands import Bot
from discord.ext import commands
from discord import Member
from discord import Guild
from discord import User
from reaction_roles import *
import logging

logger = logging.getLogger(__name__)
_defaultreason = "No Reason has been given"
channelid = 967052078209986580
"""
Use k!kick @user reason to kick someone using kanao
"""
@commands.command()
@commands.has_permissions(kick_members = True)
async def kick(ctx,member:Member,*,_reason = None):
    if (_reason == None):
        _reason = _defaultreason
#if channel isn't provided, kanao will not be able to kick/ban
    _editLogChannel = ctx.bot.get_channel(channelid)
    logger.info(f'User {ctx.author.name} Kicked : {member}.')
    await _editLogChannel.send(f'user {ctx.author.name} has kicked user {member}')
    #reason has to be supplied with rea424969344687144965son = _reason, due to the function not working otherwise
    #same with ban
    await member.kick(reason = _reason)
    await ctx.send(f'{member} has been kicked')

@kick.error
async def kick_error(ctx,error):
    logger.error(f'Kick error for User: {ctx.author.name}, who tried to kick someone: {error}')
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
    _editLogChannel = ctx.bot.get_channel(channelid)
    logger.info(f'user {ctx.author.name} has banned user {member}')
    await _editLogChannel.send(f'user {ctx.author.name} has banned user {member}')
    await member.ban(reason = _reason)
    await ctx.send(f'{member} has been banned')

@ban.error
async def ban_error(ctx,error):
    logger.error(f"Ban Error for user '{ctx.author.name}' While trying to ban someone: {error}")
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("No perms? 🤨", delete_after=10, reference=ctx.message)


@commands.command()
@commands.has_permissions(ban_members = True)
async def unban(ctx,*,member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user

        if(user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            logger.info(f'user {ctx.author.name} has unbanned {user.name}{user.discriminator}')
            _editLogChannel = ctx.bot.get_channel(channelid)
            await _editLogChannel.send(f'user {ctx.author.name} hat {user.name}{user.discriminator} entbannt')
            await ctx.send(f'User {user.mention}Wurde von {ctx.author.name} Entbannt.Bleib artig!')
            return 
@unban.error
async def unban_error(ctx,error):
    logger.error(f"Unban Error for User '{ctx.author.name}'While trying to unban someone")
def setup(bot: Bot):
    bot.add_command(kick)
    bot.add_command(ban)
    bot.add_command(unban)