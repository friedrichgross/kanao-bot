"""
Bot created by Friedrich Gross 16.04.22
Intent is to replace external bots in our FS Servers

Licensed under GPL-3.0-only
"""

import discord
import os
import logging
from dotenv import load_dotenv

from reaction_roles import SERVER_ID
import roles
import misc
import message_events
import purge

logger = logging.getLogger(__name__)

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

"""

The main class for Kanao, derived from the discord.client class

"""
class kanao(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.messages = True
        intents.message_content = True
        super().__init__(intents=intents)
        self.synced = False # to make sure we only sync our commands once

    async def on_ready(self):
        await self.wait_until_ready()
        logger.info(f'{bot.user} has connected to Discord')
        if not self.synced:
            logger.info(f"Now syncing slash-commands to Server")
            await cmd_tree.sync()
            self.synced = True
    
        if SERVER_ID is not None:
            logger.info("Checking if we missed any reaction roles while offline")
            await roles.restore_reaction_roles(bot)
        else:
            logger.warning("No SERVER_ID set, skipping reaction role restoration")

        await bot.change_presence(activity=discord.Game(name="Now with slash-commands!"))
        logger.info(f'{bot.user} has finished initialising')


bot = kanao()
cmd_tree = discord.app_commands.CommandTree(bot)

# load functionality that is defined in other modules:
roles.setup(bot, cmd_tree)
message_events.setup(bot, cmd_tree)
purge.setup(bot, cmd_tree)
misc.setup(bot, cmd_tree)

def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s - [%(funcName)s() @ %(module)s.py:%(lineno)d] %(message)s', datefmt='%d-%m-%y %H:%M:%S', level=logging.INFO)
    bot.run(BOT_TOKEN)


if __name__ == "__main__":
    main()
