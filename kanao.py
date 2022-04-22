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
bot.load_extension("message_events")
bot.load_extension("purge")
bot.load_extension("misc")


@bot.command(aliases=["h", "help"])
async def custom_help(ctx):
    logger.info(f"User '{ctx.author.name}' used the help command in channel '{ctx.channel.name}'")
    await ctx.send('```' + 'k!av @mention to get someones pfp\n' +
                   'k!purge n to delete the last n+1 messages (mod+ only, <= 100 max) \n' +
                    'k!pingRole @role to ping that role (make sure to put a spacebar after the role, ' +
                    'so it looks like a ping!)\n' +
                    '```', reference=ctx.message)


def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s - [%(funcName)s() @ %(module)s.py:%(lineno)d] %(message)s', datefmt='%d-%m-%y %H:%M:%S', level=logging.INFO)
    bot.run(BOT_TOKEN)


if __name__ == "__main__":
    main()
