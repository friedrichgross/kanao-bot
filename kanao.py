"""
Bot created by Friedrich Gross 16.04.22
Intent is to replace external bots in our FS Servers

Licensed under GPL-3.0-only
"""
from typing import Any

import discord
import os
import logging
from dotenv import load_dotenv
from discord.ext import commands
from discord.utils import get

from reaction_roles import *

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

Check for missed reactions while offline

"""


@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord')
    if SERVER_ID is not None:
        logger.info("Checking if we missed any selfroles while offline")
        await restore_reaction_roles()
    else:
        logger.warning("No SERVER_ID set, skipping selfrole restoration")
    logger.info(f'{bot.user} has finished initialising')
    await bot.change_presence(activity=discord.Game(name="k!help"))

"""

Selfroles add

"""

@bot.event
async def on_raw_reaction_add(payload):
    _role = await get_role(payload)
    if _role is not None:
        try:
            await payload.member.add_roles(_role)
            logger.info(f"Added role '{_role.name}' to user '{payload.member.name}'")
        except discord.HTTPException:
            logger.error("HTTPException")
            payload.channel.send("It appears the discord API is not available.\nPlease contact an admin if the problem persists.", delete_after=30)
            pass

"""

Selfroles remove

"""
@bot.event
async def on_raw_reaction_remove(payload):
    role = await get_role(payload)

    if role is not None:
        try:
            guild = bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            if member is None:
                logger.error(f"Could not find user '{member.name}'")
                return

            await member.remove_roles(role)
            logger.info(f"Removed role '{role.name}' from user '{member.name}'")
        except discord.HTTPException:
            logger.error("HTTPException")
            payload.channel.send("It appears the discord API is not available.\nPlease contact an admin if the problem persists.", delete_after=30)
            pass

"""

check if a message tries to role mention without using k!pingRole
advise user if that's the case
Extensible for further message checks

"""


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    ctx = await bot.get_context(message)
    if ctx.valid:
        await bot.process_commands(message)
        return
    if ctx.message.raw_role_mentions:
        if not ctx.author.guild_permissions.mention_everyone:
            logger.warning(f"User {ctx.author.name} tried to use raw role mentions without permissions in channel '{ctx.channel.name}'")
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

        for msg in payload.cached_messages:
            await _modLogChannel.send("```" + msg.author.name + ":\n" + msg.content + "\n" + "```")

    except:
        await _modLogChannel.send("Failed getting any cached messages.")

@bot.command(aliases=['h'])
async def help(ctx):
    logger.info(f"User '{ctx.author.name}' used the help command in channel '{ctx.channel.name}'")
    await ctx.send( '```' + 'k!av @mention to get someones pfp\n' + 
                    'k!purge n to delete the last n+1 messages (mod+ only, <= 100 max) \n' + 
                    'k!pingRole @role to ping that role (make sure to put a spacebar after the role, so it looks like a ping!)\n' + 
                    '```', reference=ctx.message)

@bot.command()
async def cat(ctx, arg='UwU'):
    # Sauce: https://http.cat
    valid_http_status_codes = [
     "100", "101", "102", "200", "201", "202", "203", "204", "206",
     "207", "300", "301", "302", "303", "304", "305", "307", "308",
     "400", "401", "402", "403", "404", "405", "406", "407", "408",
     "409", "410", "411", "412", "413", "414", "415", "416", "417",
     "418", "420", "421", "422", "424", "425", "426", "429", "431",
     "444", "450", "451", "497", "498", "499", "500", "501", "502",
     "503", "504", "506", "507", "508", "509", "510", "511", "521",
     "523", "525", "599"
    ]

    if arg in valid_http_status_codes:
        await ctx.send(f'https://http.cat/{arg}')
        logger.info(f"Sent http-cat with statuscode '{arg}' for user '{ctx.author.name}' in channel '{ctx.channel.name}'")
    else:
        logger.warning(f"Invalid status code ({arg}) from user '{ctx.author.name}' in channel '{ctx.channel.name}'")
        await ctx.send('You must supply a valid numeric http status code!')
        await ctx.send('https://http.cat/400')

"""

allows purging of up to 100 messages. only mods and admins.
factors in the commanding messages automatically 

"""


@bot.command()
@commands.has_any_role("Moderator", "Admin")
async def purge(ctx, arg):
    to_delete = int(arg) + 1
    delete_list = []
    async for message in ctx.history(limit=to_delete):
        delete_list.append(message)
    logger.info(f"Purging {to_delete} messages for user '{ctx.author.name}' in channel '{ctx.channel.name}'")
    await ctx.channel.delete_messages(delete_list)

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
    roleRawID = ctx.message.raw_role_mentions       # this returns a LIST, not an INT
    if not roleRawID:                               # will be empty if @everyone/@here or if no mention (duh)
        logger.warning(f"User '{ctx.author.name}' tried to ping with empty roleRawID (@everone/@here/no mention) in channel '{ctx.channel.name}'")
        await ctx.send("Make sure to put @role and a spacebar behind, so it looks like a ping. \nI wont ping @ everyone or @ here.", reference=ctx.message)
        return

    roleName = get(ctx.guild.roles, id=roleRawID[0])
    
    if roleName in ctx.author.roles:
        logger.info(f"Pinging role '{roleName}' for user '{ctx.author.name}' in channel '{ctx.channel.name}'")
        await ctx.send('<@&' + str(roleRawID[0]) + '>', reference=ctx.message)
    else :
        logger.warning(f"User '{ctx.author.name}' tried to ping role '{roleName}' in channel '{ctx.channel.name}', but they don't have that role")
        await ctx.send('You need to have the role yourself to have me ping it!')


"""

gives the mentioned users pfp

"""


@bot.command(aliases=['av'])
async def avatar(ctx):
    for user in ctx.message.mentions:
        logger.info(f"Showing avatar from user '{user}' for user '{ctx.author.name}' in channel '{ctx.channel.name}'")
        await ctx.send(user.avatar_url)

"""

Retrieves a role for a given reaction by looking up the emoji in the REACTION_ROLES_MAP list.
Also clears reaction-emojis that are not in the list from the message

"""
async def get_role(payload):
    if payload.message_id in REACTION_ROLE_MSG_IDS.values():
        guild = bot.get_guild(payload.guild_id)
        if guild is None:
            logger.error("No guild/server??")
            return

        try:
            return discord.utils.get(_guild.roles, name=REACTION_ROLES_MAP[payload.emoji.name])
        except KeyError:
        print("Reaction roles: Role for Emoji '" + payload.emoji.name + "' not found, removing reaction.")
            channel = bot.get_channel(payload.channel_id)
            logger.warning(f"User '{payload.member.name}' reacted with '{payload.emoji.name}' in channel '{channel.name}', but no role was found for that emoji. Removing reaction")
            msg = await channel.fetch_message(payload.message_id)
            for reaction in msg.reactions:
                if str(reaction.emoji) == str(payload.emoji):
                    await reaction.clear()
                print("Reaction Roles: Cleared reaction")
                return
 

"""

Checks if all users who reacted to the selfroles-msg have the corresponding role & gives it to them if they don't.
Also clears all reactions that are not corresponding to a role.

"""
async def restore_reaction_roles():
    for channel_id in REACTION_ROLE_MSG_IDS.keys():
        channel = bot.get_channel(channel_id)
        if channel is None:
            logger.error(f"Could not restore reaction roles: channel_id '{channel_id}' not found. Quitting")
            return

        try:
            msg = await channel.fetch_message(REACTION_ROLE_MSG_IDS[channel_id])
        except Exception as e:
            logger.error(f"Could not fetch channel: {e}")
            return

        guild = bot.get_guild(int(SERVER_ID))
        for reaction in _msg.reactions:
            try:
                role = discord.utils.get(guild.roles, name=REACTION_ROLES_MAP[reaction.emoji])
            except KeyError:
                logger.warning(f"Role for Emoji '{reaction.emoji.name}' sent by user '{member.name}' in channel {channel.name} not found, removing reaction")
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
                    if not role in member.roles:
                        logger.info(f"User '{member.name}' does not yet have the '{REACTION_ROLES_MAP[reaction.emoji]}' role, but has sent the reaction for it. Adding role now")
                        try:
                            await member.add_roles(role)
                        except discord.HTTPException:
                            logger.error("HTTPException")
                            pass

            except discord.HTTPException:
                logger.error("HTTPException")

def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s - [%(funcName)s() @ %(module)s.py:%(lineno)d] %(message)s', datefmt='%d-%m-%y %H:%M:%S', level=logging.INFO)
    bot.run(BOT_TOKEN)


if __name__ == "__main__":
    main()