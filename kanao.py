"""
Bot created by Friedrich Gross 16.04.22
Intent is to replace external bots in our FS Servers

Licensed under GPL-3.0-only
"""

import discord
import os
import logging
from dotenv import load_dotenv
from discord.ext import commands
from discord.utils import get

logger = logging.getLogger(__name__)

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

"""

get intents from discord, privileged intents are needed

"""

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='k!', intents=intents, help_command=None)

"""

load functionality that is defined in other modules
"""
bot.load_extension("roles")

"""

check if a message tries to role mention without using k!pingRole
advise user if that's the case
Extensible for further message checks

"""


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    _ctx = await bot.get_context(message)
    if _ctx.valid:
        await bot.process_commands(message)
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


@bot.event
async def on_message_edit(before, after):
    if before.author.bot:
        return
    _editLogChannel = bot.get_channel(MESSAGE_EDIT_LOG)
    print(_editLogChannel)
    await _editLogChannel.send("```EDIT EVENT:\n\n" + "User: " + before.author.name + "\n\n" +
                        "Before: " + before.content + "\n\n" +
                        "After: " + after.content + "```")

""" 

message delete event
same things as with on_message_edit apply

"""
@bot.event
async def on_message_delete(message):
    _editLogChannel = bot.get_channel(MESSAGE_EDIT_LOG)
    await _editLogChannel.send("```MSG DELETE EVENT:\n\n" + "User: " + message.author.name + "\n\n" +
                        "Channel: " + message.channel.name + "\n"
                        "Message: " + message.content + "```")

@bot.event
async def on_raw_bulk_message_delete(payload):
    _modLogChannel = bot.get_channel(MOD_LOG)
    _eventChannel = bot.get_channel(payload.channel_id)
    try:
        await _modLogChannel.send("```!! BULK DELETE EVENT !!" + "\n\n" + "Channel :" + _eventChannel.name + "\n\n"
                                 "Trying to get possibly cached messages: ```")
        for _msg in payload.cached_messages:
            await _modLogChannel.send("```" + _msg.author.name + ":\n" + _msg.content + "\n" + "```")

    except:
        await _modLogChannel.send("Failed getting any cached messages.")

@bot.command(aliases=["h", "help"])
async def custom_help(ctx):
    logger.info(f"User '{ctx.author.name}' used the help command in channel '{ctx.channel.name}'")
    await ctx.send('```' + 'k!av @mention to get someones pfp\n' +
                    'k!purge n to delete the last n+1 messages (mod+ only, <= 100 max) \n' + 
                    'k!pingRole @role to ping that role (make sure to put a spacebar after the role, so it looks like a ping!)\n' + 
                    '```', reference=ctx.message)

"""

allows purging of up to 100 messages. only mods and admins.
factors in the commanding messages automatically 

"""

@bot.command()
@commands.has_any_role("Moderator", "Admin")
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

"""

method to make the user use the bot to ping roles.
this ensures we can log pings to roles, and that people only ping roles they have themselves.

"""


@bot.command(aliases=['pr'])
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

@bot.command(aliases=['av'])
async def avatar(ctx):
    for _user in ctx.message.mentions:
        logger.info(f"Showing avatar from user '{_user}' for user '{ctx.author.name}' in channel '{ctx.channel.name}'")
        await ctx.send(_user.avatar_url)

@bot.command()
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


def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s - [%(funcName)s() @ %(module)s.py:%(lineno)d] %(message)s', datefmt='%d-%m-%y %H:%M:%S', level=logging.INFO)
    bot.run(BOT_TOKEN)


if __name__ == "__main__":
    main()
