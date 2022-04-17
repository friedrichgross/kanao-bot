"""
Bot created by Friedrich Gross 16.04.22
Intent is to replace external bots in our FS Servers

Licensed under GPL-3.0-only
"""

import discord
import os
import re
from dotenv import load_dotenv
from discord.ext import commands
from discord.utils import get

from reaction_roles import *

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
SERVER_ID = int(os.getenv('SERVER_ID'))

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='k!', intents=intents, help_command=None)


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    if SERVER_ID is not None:
        await restore_reaction_roles()
    print(f'{bot.user} has finished initialising!')

@bot.event
async def on_raw_reaction_add(payload):
    role = await get_role(payload)
    if role is not None:
        try:
            await payload.member.add_roles(role)
            print("Selfroles: Added role '" + role.name + "' to user '" + payload.member.name + "'.")
        except discord.HTTPException:
            # TODO: Errorhandling
            pass
    else:
        print("Role not implemented??")

@bot.event
async def on_raw_reaction_remove(payload):
    role = await get_role(payload)

    if role is not None:
        try:
            guild = bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            if member is None:
                print("Could not find user")
                return

            await member.remove_roles(role)
            print("Selfroles: Removed role '" + role.name + "' from user '" + member.name + "'.")
        except discord.HTTPException:
            # TODO: Error handling
            pass

    else:
        print("Role not implemented??")

@bot.command()
async def help(ctx):
    await ctx.send( '```' + 'k!av @mention to get someones pfp\n' + 
                    'k!purge n to delete the last n+1 messages (mod+ only, <= 100 max) \n' + 
                    'k!pingRole @role to ping that role (make sure to put a spacebar after the role, so it looks like a ping!)' + '```')

@bot.command()
@commands.has_any_role("Moderator", "Admin")
async def purge(ctx, arg):
    to_delete = int(arg) + 1
    delete_list = []
    async for message in ctx.history(limit=to_delete):
        delete_list.append(message)
    await ctx.channel.delete_messages(delete_list)

@purge.error
async def purge_error(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.send("No perms? 🤨", delete_after=5)

@bot.command()
async def pingRole(ctx, arg):
    roleRawID = ctx.message.raw_role_mentions       # this returns a LIST, not an INT
    if not roleRawID:                               # will be empty if @everyone/@here
        await ctx.send("Youre not allowed to do that!")
        return                                      

    roleName = get(ctx.guild.roles , id=roleRawID[0])
    
    if roleName in ctx.author.roles:
        await ctx.send('<@&' + str(roleRawID[0]) + '>', reference=ctx.message)
    else :
        await ctx.send('You need to have the role yourself to have me ping it!')

@bot.command(name='av')
async def avatar(ctx):
    for user in ctx.message.mentions:
        await ctx.send(user.avatar_url)

async def get_role(payload):
    if payload.message_id in reaction_role_msg_ids.values():
        guild = bot.get_guild(payload.guild_id)
        if guild is None:
            print("No guild/server??")
            # TODO: Logging
            return

        try:
            return discord.utils.get(guild.roles, name=reaction_roles[payload.emoji.name])
        except KeyError:
            print("Role for Emoji '" + payload.emoji.name + "' not found, removing reaction.")
            channel = bot.get_channel(payload.channel_id)
            msg = await channel.fetch_message(payload.message_id)
            for reaction in msg.reactions:
                if str(reaction.emoji) == str(payload.emoji):
                    await reaction.clear()
            print("Cleared reaction")
            return

async def restore_reaction_roles():
    for channel_id in reaction_role_msg_ids.keys():
        channel = bot.get_channel(channel_id)
        msg = await channel.fetch_message(reaction_role_msg_ids[channel_id])
        guild = bot.get_guild(SERVER_ID)

        for reaction in msg.reactions:
            try:
                async for member in reaction.users():
                    # Check if user already has the role:
                    try:
                        role = discord.utils.get(guild.roles, name=reaction_roles[reaction.emoji])
                    except KeyError:
                        print("Role for Emoji '" + reaction.emoji.name + "' not found, removing reaction.")
                        await reaction.clear()
                        print("Cleared reaction")
                        continue

                    if not role in member.roles:
                        print("User '" + member.name + "' does not yet have the '" + reaction.emoji + "' role , adding now...")
                        try:
                            await member.add_roles(role)
                            print("Selfroles-restore: Added role '" + role.name + "' to user '" + member.name + "'.")
                        except discord.HTTPException:
                            # TODO: Error handling
                            pass

            except discord.HTTPException:
                print("Couldn't fetch users for reaction-roles")

bot.run(BOT_TOKEN)
