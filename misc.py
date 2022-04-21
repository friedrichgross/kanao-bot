from discord.ext.commands import Bot
from discord.ext import commands
from discord.utils import get
import logging

logger = logging.getLogger(__name__)
"""

method to make the user use the bot to ping roles.
this ensures we can log pings to roles, and that people only ping roles they have themselves.

"""
@commands.command(aliases=['pr'])
async def pingRole(ctx, arg):
    _raw_role_ID = ctx.message.raw_role_mentions       # this returns a LIST, not an INT
    if not _raw_role_ID:                               # will be empty if @everyone/@here or if no mention (duh)
        logger.warning(f"User '{ctx.author.name}' tried to ping with empty _raw_role_ID (@everone/@here/no mention) in channel '{ctx.channel.name}'")
        await ctx.send("Make sure to put @role and a spacebar behind, so it looks like a ping. \nI wont ping @ everyone or @ here.", reference=ctx.message)
        return

    _roleName = get(ctx.guild.roles, id=_raw_role_ID[0])
    
    if _roleName in ctx.author.roles:
        logger.info(f"Pinging role '{_roleName}' for user '{ctx.author.name}' in channel '{ctx.channel.name}'")
        await ctx.send('<@&' + str(_raw_role_ID[0]) + '>', reference=ctx.message)
    else :
        logger.warning(f"User '{ctx.author.name}' tried to ping role '{_roleName}' in channel '{ctx.channel.name}', but they don't have that role")
        await ctx.send('You need to have the role yourself to have me ping it!')


"""

gives the mentioned users pfp

"""

@commands.command(aliases=['av'])
async def avatar(ctx):
    for _user in ctx.message.mentions:
        logger.info(f"Showing avatar from user '{_user}' for user '{ctx.author.name}' in channel '{ctx.channel.name}'")
        await ctx.send(_user.avatar_url)

async def cat(ctx, arg='UwU'):
    # Sauce: https://http.cat
    _valid_http_status_codes = [
     "100", "101", "102", "200", "201", "202", "203", "204", "206",
     "207", "300", "301", "302", "303", "304", "305", "307", "308",
     "400", "401", "402", "403", "404", "405", "406", "407", "408",
     "409", "410", "411", "412", "413", "414", "415", "416", "417",
     "418", "420", "421", "422", "424", "425", "426", "429", "431",
     "444", "450", "451", "497", "498", "499", "500", "501", "502",
     "503", "504", "506", "507", "508", "509", "510", "511", "521",
     "523", "525", "599"
    ]

    if arg in _valid_http_status_codes:
        await ctx.send(f'https://http.cat/{arg}')
        logger.info(f"Sent http-cat with statuscode '{arg}' for user '{ctx.author.name}' in channel '{ctx.channel.name}'")
    else:
        logger.warning(f"Invalid status code ({arg}) from user '{ctx.author.name}' in channel '{ctx.channel.name}'")
        await ctx.send('You must supply a valid numeric http status code!')
        await ctx.send('https://http.cat/400')


def setup(bot: Bot):
    bot.add_command(pingRole)
    bot.add_command(avatar)
    bot.add_command(cat)
