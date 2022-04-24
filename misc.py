from discord.ext.commands import Bot
from discord.ext.commands import Cog
from discord.ext import commands
from discord.utils import get
import logging


logger = logging.getLogger(__name__)


class Misc(Cog):


    def __init__(self, bot: Bot):
        self.bot = bot
    """

    method to make the user use the bot to ping roles.
    this ensures we can log pings to roles, and that people only ping roles they have themselves.

    """
    @commands.command(aliases=['pr', 'pingRole'])
    async def ping_role(self, ctx):
        _raw_role_ID = ctx.message.raw_role_mentions       # this returns a LIST, not an INT
        if not _raw_role_ID:                               # will be empty if @everyone/@here or if no mention (duh)
            logger.warning(f"User '{ctx.author.name}' tried to ping with empty _raw_role_ID " +
                           f"(@everyone/@here/no mention) in channel '{ctx.channel.name}'")
            await ctx.send("Make sure to put @role and a space bar behind, so it looks like a ping. \n" +
                           "I wont ping @ everyone or @ here.", reference=ctx.message)
            return

        _roleName = get(ctx.guild.roles, id=_raw_role_ID[0])
        
        if _roleName in ctx.author.roles:
            logger.info(f"Pinging role '{_roleName}' for user '{ctx.author.name}' in channel '{ctx.channel.name}'")
            await ctx.send('<@&' + str(_raw_role_ID[0]) + '>', reference=ctx.message)
        else :
            logger.warning(f"User '{ctx.author.name}' tried to ping role '{_roleName}' in channel '{ctx.channel.name}', " +
                           f"but they don't have that role")
            await ctx.send('You need to have the role yourself to have me ping it!', reference=ctx.message)


    """

    gives the mentioned users pfp

    """
    @commands.command(aliases=['av'])
    async def avatar(self, ctx):
        for _user in ctx.message.mentions:
            logger.info(f"Showing avatar from user '{_user}' for user '{ctx.author.name}' in channel '{ctx.channel.name}'")
            await ctx.send(_user.avatar_url, reference=ctx.message)


    @commands.command()
    async def cat(self, ctx, arg='UwU'):
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


    """ 

    precursor to warning function, sends image of kanao_gun in response to an intolerable message
    (yes i was bored)

    """
    @commands.command(aliases=["gun", "gat"])
    @commands.has_any_role("Moderator", "Admin")
    async def kanao_gun(self, ctx):
        if ctx.message.reference:
            await ctx.send("https://media.discordapp.net/attachments/863157204705345566/965595907544469504/unknown.png",
                           reference=ctx.message.reference)
            await ctx.message.delete()
        else:
            await ctx.send("No reference provided", reference=ctx.message, delete_after=5)


    @kanao_gun.error
    async def kanao_gun_error(self, ctx, error):
        logger.error(f"Kanao Gun Error for user '{ctx.author.name}' in channel '{ctx.channel.name}': {error}")
        if isinstance(error, commands.MissingAnyRole):
            await ctx.send("No perms? 🤨", delete_after=10, reference=ctx.message)


def setup(bot: Bot):
    bot.add_cog(Misc(bot))
