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


class RolesFailure(commands.CheckFailure):
    pass

def roles_config():
    async def predicate(ctx):
        playing_role = get_role('playing_role') is not None
        it_role = get_role('it_role') is not None
        not_it_role = get_role('not_it_role') is not None
        if not playing_role and it_role and not_it_role:
            raise RolesFailure('`CONFIGURATION ERROR: You are missing a guild and/or role id.`')
        return True
    return commands.check(predicate)


# Role manager
def get_role(role):
    if config.cget('guild_id') is None:
        return None
    if config.cget(role) is None:
        return None
    return bot.get_guild(config.cget('guild_id')).get_role(config.cget(role))


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


@playing.error
async def playing_error(ctx, error):
    if isinstance(error, RolesFailure):
        await ctx.reply(error)
    else:
        await ctx.reply("Oops, you can't do that while the game is active.")


# Tag commands

@bot.command()
@game_not_active()
@game_not_paused()
async def start(ctx):
    config.cset('start_time', logger.log('START'))
    await ctx.reply("@Playing\nGame has started!")


@start.error
async def start_error(ctx, error):
    await ctx.reply("Oops, you can't do that right now!")


@bot.command()
@game_active()
async def end(ctx):
    config.cset('end_time', logger.log('END'))
    # logger.user_set_all('Playing', 'False')
    await ctx.reply("@Playing\nGame has ended!")


@end.error
async def end_error(ctx, error):
    await ctx.reply("Oops, you can't do that right now!")


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
    await ctx.reply("@Playing\n" + tagged.mention + " has been tagged by " + ctx.author.mention + ".")


@tag.error
async def tag_error(ctx, error):
    if isinstance(error, RolesFailure):
        await ctx.reply(error)
    else:
        ctx.reply("Oops, you can't do that right now!")


@bot.command()
async def leaderboard(ctx):
    reply = leaderboard.to_string(logger.get_leaderboard())
    await ctx.reply(reply)


# Owner and debug commands

@bot.command()
@commands.is_owner()
async def server_reset(ctx):
    return


@bot.command()
@commands.is_owner()
async def leaderboard_reset(ctx):
    return


@bot.command()
@commands.is_owner()
async def config_reset(ctx):
    return


@bot.command()
@commands.is_owner()
async def toggle_debug(ctx):
    return


@bot.command()
@commands.is_owner()
async def export(ctx):
    return


# Global checks
@bot.check
async def globally_block_dms(ctx):
    return ctx.guild is not None

bot_token = config.cget('bot_token')
if bot_token != 'NULL':
    bot.run(bot_token)
