import discord
from discord.ext import commands
from discord.ext import tasks
import asyncio
import time
import config
import logger
import leaderboard

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', description="TagBot", help_command=None, intents=intents)


@bot.event
async def on_ready():
    print('Logged in as', bot.user)


# Command Checks
def game_active():
    async def predicate(ctx):
        return config.cget('active')
    return commands.check(predicate)


def game_not_active():
    # there's probably a better way of doing this
    async def predicate(ctx):
        return not config.cget('active')
    return commands.check(predicate)


def game_paused():
    async def predicate(ctx):
        return config.cget('paused')
    return commands.check(predicate)


def game_not_paused():
    async def predicate(ctx):
        return not config.cget('paused')
    return commands.check(predicate)


def game_not_cooldown():
    async def predicate(ctx):
        last_tag = logger.get_last_log('Tag')
        is_cooldown = (int(time.time()) - last_tag) < config.cget('cooldown')
        return not is_cooldown
    return commands.check(predicate)


def is_playing():
    async def predicate(ctx):
        return logger.user_check(ctx.author, 'Playing')
    return commands.check(predicate)


def is_it():
    async def predicate(ctx):
        return logger.user_check(ctx.author, 'It')
    return commands.check(predicate)


def is_debug():
    async def predicate(ctx):
        return config.cget('debug_mode')
    return commands.check(predicate)

class RolesFailure(commands.CheckFailure):
    pass

def roles_config():
    async def predicate(ctx):
        playing_role = get_role('playing_role') is not None
        it_role = get_role('it_role') is not None
        not_it_role = get_role('not_it_role') is not None
        if not playing_role and it_role and not_it_role:
            raise RolesFailure('`CONFIG ERROR: You are missing one or more role IDs.`')
        return True
    return commands.check(predicate)


# Role manager
def get_role(role_name):
    if config.cget('guild_id') is None:
        raise RolesFailure('`CONFIG ERROR: You are missing a guild ID.`')
    role_id = config.cget(role_name)
    if role_id is None:
        raise RolesFailure('`CONFIG ERROR: You are missing one or more role IDs.`')
    guild = bot.get_guild(config.cget('guild_id'))
    role = discord.utils.get(guild.roles, id=role_id)
    return role


# Config commands

@bot.command()
@game_not_active()
@game_not_paused()
@roles_config()
async def playing(ctx):
    reply = "Set user " + ctx.author.mention + " to "
    if logger.user_set(ctx.author, 'Playing'):
        await ctx.author.add_roles(get_role('playing_role'))
        reply += "playing."
    else:
        await ctx.author.remove_roles(get_role('playing_role'))
        reply += "not playing."
    await ctx.reply(reply)


# Tag commands

@bot.command()
@game_not_active()
@game_not_paused()
async def start(ctx):
    config.cset('active', True)
    config.cset('start_time', logger.log('START'))
    await ctx.send("@Playing\nGame has started!")


@bot.command()
@game_active()
async def end(ctx):
    config.cset('active', False)
    config.cset('end_time', logger.log('END'))
    # logger.user_set_all('Playing', 'False')
    await ctx.send("@Playing\nGame has ended!")


@bot.command()
@game_active()
@game_not_paused()
async def pause(ctx):
    return


@bot.command()
@game_not_active()
@game_paused()
async def resume(ctx):
    return


@bot.command()
@game_active()
@game_not_paused()
@is_playing()
@is_it()
@roles_config()
async def tag(ctx, *, tagged: discord.Member):
    logger.log('TAG', tagged)
    await ctx.author.add_roles(get_role('not_it_role'))
    await ctx.author.remove_roles(get_role('it_role'))
    logger.user_set(ctx.author, 'It')
    await tagged.add_roles(get_role('it_role'))
    await tagged.remove_roles(get_role('not_it_role'))
    logger.user_set(tagged, 'It')
    await ctx.send("@Playing\n" + tagged.mention + " has been tagged by " + ctx.author.mention + ".")


@playing.error
@start.error
@end.error
@tag.error
async def game_error(ctx, error):
    if isinstance(error, RolesFailure):
        await ctx.reply(error)
    elif isinstance(error, commands.CheckFailure):
        await ctx.reply("Oops, you can't do that right now!")
    else:
        await ctx.reply("Oops, something went wrong.")


@bot.command()
async def leaderboard(ctx):
    reply = leaderboard.to_string(logger.get_leaderboard())
    await ctx.send(reply)


# Owner and debug commands

@bot.command()
@commands.is_owner()
@is_debug()
async def server_reset(ctx):
    return


@bot.command()
@commands.is_owner()
@is_debug()
async def leaderboard_reset(ctx):
    return


@bot.command()
@commands.is_owner()
@is_debug()
async def config_dump(ctx):
    cdump = "config.ini\n"
    with open("config.ini", "r") as cfile:
        cdump += cfile.read()
    await ctx.send('```' + cdump[:-73] + '```')


@bot.command()
@commands.is_owner()
@is_debug()
async def config_reset(ctx):
    config.reset()
    await ctx.send("```'config.ini' reset.\nWARNING: this command does not reset 'initial_config', "
                   "'guild_settings', or 'bot_token'.```")


@bot.command()
@commands.is_owner()
@is_debug()
async def export(ctx):
    ctx.send(file='logs.db')


@bot.command()
@commands.is_owner()
@is_debug()
async def role(ctx, *, added_role:discord.Role):
    if added_role.name == 'Playing':
        config.cset('playing_role', added_role.id)
        await ctx.send('`Successfully added playing_role id.`')
    elif added_role.name == 'It':
        config.cset('it_role', added_role.id)
        await ctx.send('`Successfully added it_role id.`')
    elif added_role.name == 'Not It':
        config.cset('not_it_role', added_role.id)
        await ctx.send('`Successfully added not_it_role id.`')
    else:
        await ctx.send('`Unrecognized role. Try manually adding role id.`')


@bot.command()
@commands.is_owner()
async def toggle_debug(ctx):
    if config.cget('debug_mode'):
        toggle = False
    else:
        toggle = True
    config.cset('debug_mode', toggle)
    await ctx.send('`Debug mode set to ' + str(toggle) + '`')


@server_reset.error
@leaderboard_reset.error
@config_dump.error
@config_reset.error
@export.error
async def debug_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.reply("Oops, you can't do that right now! Is debug mode enabled?")
        return
    await ctx.reply("Oops, something went wrong.")


# Global checks
@bot.check
async def globally_block_dms(ctx):
    return ctx.guild is not None


bot_token = config.cget('bot_token')
if bot_token != 'NULL':
    bot.run(bot_token)
else:
    print("BOT TOKEN IS MISSING")
