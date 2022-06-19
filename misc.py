import discord
import logging

logger = logging.getLogger(__name__)


"""

method to make the user use the bot to ping roles.
this ensures we can log pings to roles, and that people only ping roles they have themselves.

"""
@discord.app_commands.command(name="ping", description="Pings a given Role in the current channel")
@discord.app_commands.describe(role="The role you want to ping")
async def ping_role(interaction: discord.Interaction, role: discord.Role):
    if role.name == "@everyone":
        logger.warning(f"User '{interaction.user.name}' tried to ping {role} in channel '{interaction.channel.name}'")
        await interaction.response.send_message(f"Role '{role}' not pingable (I wont ping @everyone or @here)", ephemeral=True)
        return

    if role in interaction.user.roles:
        logger.info(f"Pinging role '{role.name}' for user '{interaction.user.roles}' in channel '{interaction.channel.name}'")
        await interaction.response.send_message('<@&' + str(role.id) + '>')
    else :
        logger.warning(f"User '{interaction.user.name}' tried to ping role '{role.name}' in channel '{interaction.channel.name}', " +
                       f"but they don't have that role")
        await interaction.response.send_message('You need to have the role yourself to have me ping it!', ephemeral=True)


"""

gives the mentioned users pfp

"""
@discord.app_commands.command(name="avatar", description="Postet den Avatar eines Nutzers im Channel")
@discord.app_commands.describe(user="The user whos avatar should be shown")
async def avatar(interaction, user: discord.User):
    logger.info(f"Trying to show avatar from user '{user.name}' for user '{interaction.user.name}' in channel '{interaction.channel.name}'")
    if user.avatar:
        await interaction.response.send_message(user.avatar.url)
    else:
        logger.info(f"Failed to show avatar from '{user.name}' for user '{interaction.user.name}' in channel '{interaction.channel.name}' (No Avatar found)")
        await interaction.response.send_message(f"User {user.name} has no avatar for me to show.", ephemeral=True)


@discord.app_commands.command(name="cat", description="Postet eine HTTP-Status-Cat im Channel")
@discord.app_commands.describe(code="HTTP Status Code to send")
async def cat(interaction, code: int):
    # Sauce: https://http.cat
    _valid_http_status_codes = [
     100, 101, 102, 200, 201, 202, 203, 204, 206,
     207, 300, 301, 302, 303, 304, 305, 307, 308,
     400, 401, 402, 403, 404, 405, 406, 407, 408,
     409, 410, 411, 412, 413, 414, 415, 416, 417,
     418, 420, 421, 422, 424, 425, 426, 429, 431,
     444, 450, 451, 497, 498, 499, 500, 501, 502,
     503, 504, 506, 507, 508, 509, 510, 511, 521,
     523, 525, 599
    ]

    if code in _valid_http_status_codes:
        await interaction.response.send_message(f'https://http.cat/{code}')
        logger.info(f"Sent http-cat with statuscode '{code}' for user '{interaction.user.name}' in channel '{interaction.channel.name}'")
    else:
        logger.warning(f"Invalid status code ({code}) from user '{interaction.user.name}' in channel '{interaction.channel.name}'")
        await interaction.response.send_message(f"You must supply a valid numeric http status code! ``{code}`` is invalid. https://http.cat/400", ephemeral=True)


""" 

precursor to warning function, sends image of kanao_gun in response to an intolerable message
(yes i was bored)

"""
@discord.app_commands.context_menu(name="gun")
@discord.app_commands.checks.has_any_role("Moderator", "Admin")
async def kanao_gun(interaction, msg: discord.Message):
    await msg.delete()
    await interaction.response.send_message(f"<@{msg.author.id}> https://media.discordapp.net/attachments/863157204705345566/965595907544469504/unknown.png")


@kanao_gun.error
async def kanao_gun_error(interaction, error):
    logger.error(f"Kanao Gun Error for user '{interaction.user.name}' in channel '{interaction.channel.name}': {error}")
    if isinstance(error, discord.app_commands.MissingAnyRole):
        await interaction.response.send_message("No perms? 🤨", ephemeral=True)


def setup(bot, cmd_tree):
    cmd_tree.add_command(ping_role)
    cmd_tree.add_command(avatar)
    cmd_tree.add_command(cat)
    cmd_tree.add_command(kanao_gun)

