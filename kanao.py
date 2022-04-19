"""
Bot created by Friedrich Gross 16.04.22
Intent is to replace external bots in our FS Servers

Licensed under GPL-3.0-only
"""
from typing import Any

import discord
import os
import re
from dotenv import load_dotenv
from discord.ext import commands
from discord.utils import get

from reaction_roles import *

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
    print(f'{bot.user} has connected to Discord!')
    if SERVER_ID is not None:
        print("Checking if we missed any reaction roles while offline...")
        await restore_reaction_roles()
    else:
        print("No SERVER_ID set, skipping reaction-role restoration.")
    print(f'{bot.user} has finished initialising!')
    await bot.change_presence(activity=discord.Game(name="k!help"))


@bot.event
async def on_raw_reaction_add(payload):
    _role = await get_role(payload)
    if _role is not None:
        try:
            await payload.member.add_roles(_role)
            print("Reaction roles: Added role '" + _role.name + "' to user '" + payload.member.name + "'.")
        except discord.HTTPException:
            channel = bot.get_channel(payload.channel_id)
            channel.send(
                "It appears the discord API is not available.\nPlease contact an admin if the problem persists.",
                delete_after=30)
            pass


@bot.event
async def on_raw_reaction_remove(payload):
    role = await get_role(payload)

    if role is not None:
        try:
            guild = bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            if member is None:
                print("Reaction roles: Could not find user")
                return

            await member.remove_roles(role)
            print("Reaction roles: Removed role '" + role.name + "' from user '" + member.name + "'.")
        except discord.HTTPException:
            channel = bot.get_channel(payload.channel_id)
            channel.send(
                "It appears the discord API is not available.\nPlease contact an admin if the problem persists.",
                delete_after=30)
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
            await message.channel.send("Normal users need to use the k!pingRole command to mention a role!",
                                       reference=message)


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

"""

help command 

"""


@bot.command(aliases=['h', help])
async def customHelp(ctx):
    await ctx.send('```' + 'k!av @mention to get someones pfp\n' +
                   'k!purge n to delete the last n+1 messages (mod+ only, <= 100 max) \n' +
                   'k!pingRole @role to ping that role (make sure to put a Space bar after the role, so it looks like '
                   'a ping!)\n' + "k!cat <http code> to call the http.cat API.\n" +
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
    await ctx.channel.delete_messages(_delete_list)



@purge.error
async def purge_error(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.send("No perms? 🤨", delete_after=10, reference=ctx.message)


"""

method to make the user use the bot to ping roles.
this ensures we can log pings to roles, and that people only ping roles they have themselves.

"""


@bot.command(aliases=['pr'])
async def pingRole(ctx, arg):
    _raw_role_id = ctx.message.raw_role_mentions  # this returns a LIST, not an INT
    if not _raw_role_id:  # will be empty if @everyone/@here or if no mention (duh)
        await ctx.send(
            "Make sure to put @role and a space bar behind, so it looks like a ping. \nI wont ping @ everyone or @ here.",
            reference=ctx.message)
        return

    _roleName = get(ctx.guild.roles, id=_raw_role_id[0])

    if _roleName in ctx.author.roles:
        await ctx.send('<@&' + str(_raw_role_id[0]) + '>', reference=ctx.message)
    else:
        await ctx.send('You need to have the role yourself to have me ping it!')


"""

gives the mentioned users pfp

"""


@bot.command(aliases=['av'])
async def avatar(ctx):
    for _user in ctx.message.mentions:
        await ctx.send(_user.avatar_url)


async def get_role(payload):
    if payload.message_id in REACTION_ROLE_MSG_IDS.values():
        _guild = bot.get_guild(payload.guild_id)
        if _guild is None:
            print("Reaction roles: No guild/server??")
            # TODO: Logging
            return

        try:
            return discord.utils.get(_guild.roles, name=REACTION_ROLES_MAP[payload.emoji.name])
        except KeyError:
            print("Reaction roles: Role for Emoji '" + payload.emoji.name + "' not found, removing reaction.")
            channel = bot.get_channel(payload.channel_id)
            msg = await channel.fetch_message(payload.message_id)
            for reaction in msg.reactions:
                if str(reaction.emoji) == str(payload.emoji):
                    await reaction.clear()
            print("Reaction Roles: Cleared reaction")
            return


async def restore_reaction_roles():
    for channel_id in REACTION_ROLE_MSG_IDS.keys():
        _channel = bot.get_channel(channel_id)
        if _channel is None:
            print("Reaction roles restore: Could not restore reaction roles: channel_id '" + str(
                channel_id) + "' not found. Quitting.")
            return

        _msg = await _channel.fetch_message(REACTION_ROLE_MSG_IDS[channel_id])
        _guild = bot.get_guild(int(SERVER_ID))

        for reaction in _msg.reactions:
            try:
                async for member in reaction.users():
                    # Skip myself bc I don't want to get EVERY role all the time
                    if member.name in REACTION_ROLE_RESTORE_IGNORED_MEMBERS:
                        # print("Selfroles-restore: Skipping member '" + member.name + "' because of REACTION_ROLE_RESTORE_IGNORED_MEMBERS.")
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
                        print(
                            "Reaction roles restore: User '" + member.name + "' does not yet have the '" + reaction.emoji + "' role , adding now...")
                        try:
                            await member.add_roles(_role)
                            print("Reaction roles restore: Added role '" + _role.name + "' to user '" + member.name + "'.")
                        except discord.HTTPException:
                            # TODO: Error handling
                            pass

            except discord.HTTPException:
                print("Reaction roles restore: Couldn't fetch users for reaction-roles")


def main():
    bot.run(BOT_TOKEN)


if __name__ == "__main__":
    main()
