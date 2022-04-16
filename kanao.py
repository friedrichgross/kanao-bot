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

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='k!', intents=intents, help_command=None)


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

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


bot.run(BOT_TOKEN)
