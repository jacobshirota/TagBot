import discord
import config
import checks
import logger


def set_bot(_bot):
    global bot
    bot = _bot


def get_role(role_name):
    from checks import RolesFailure
    if config.cget('guild_id') is None:
        raise RolesFailure('`CONFIG ERROR: You are missing a guild ID.`')
    guild = bot.get_guild(config.cget('guild_id'))
    if guild is None:
        raise RolesFailure('`CONFIG ERROR: Guild ID is incorrect`')
    role_id = config.cget(role_name)
    if role_id is None:
        raise RolesFailure('`CONFIG ERROR: You are missing one or more role IDs.`')
    role = discord.utils.get(guild.roles, id=role_id)
    return role


def start_roles(it):
    playing_role = get_role('playing_role')
    not_it_role = get_role('not_it_role')
    it_role = get_role('it_role')
    guild = bot.get_guild(config.cget('guild_id'))
    for m in guild.members:
        if playing_role not in m.roles or m == it:
            continue
        m.add_roles(not_it_role)
    it.add_roles(it_role)
    logger.user_set(it, 'It')


def end_roles():
    not_it_role = get_role('not_it_role')
    it_role = get_role('it_role')
    guild = bot.get_guild(config.cget('guild_id'))
    for m in guild.members:
        if not_it_role in m.roles:
            m.remove_roles(not_it_role)
        if it_role in m.roles:
            m.remove_roles(it_role)
    logger.user_set_all('It', "'False'")


def tag(it, not_it):
    not_it_role = get_role('not_it_role')
    it_role = get_role('it_role')

