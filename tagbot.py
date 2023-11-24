import discord
from discord.ext import commands
from discord.ext import tasks
import asyncio
import time
import config
import logger
import leaderboard
import checks
import roles
import help

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', description="TagBot", help_command=None, intents=intents)


@bot.event
async def on_ready():
    roles.set_bot(bot)
    print('Logged in as', bot.user)


# Help command

@bot.command(name='help')
async def _help(ctx, cmd=None):
    if cmd is None:
        reply = "```" + help.show_commands()
        if config.cget('debug_mode'):
            reply += help.show_debug()
        await ctx.send(reply[:-1] + "```")
    else:
        reply = '`' + help.get(cmd)
        if reply is None:
            await ctx.send("Oops, I didn't recognize that command.")
            return
        await ctx.send(reply[:-1] + "`")


# Config commands

@bot.command()
async def info(ctx):
    reply = "Game is currently "
    if config.cget('active'):
        reply += "active.\nThe game has been going on since "
        reply += time.asctime(time.localtime(config.cget('start_time')))
        reply += " (" + str(int((int(time.time())-config.cget('start_time'))/60)) + " minutes).\n"
        reply += "Nobody has been tagged "
        last_tag = logger.get_last_log('TAG')
        if last_tag is None:
            reply += "yet."
        else:
            reply += "in " + str(int((int(time.time())-int(last_tag))/60)) + " minutes."
    else:
        reply += "not active.\n"
        if config.cget('paused'):
            last_pause = logger.get_last_log('PAUSE')
            if last_pause is None:
                ctx.send("Oops, something went wrong.")
                return
            reply += "Game has been paused since " + time.asctime(time.localtime(last_pause))
        else:
            reply += "Last game ended on " + time.asctime(time.localtime(config.cget('end_time'))) + "."
    await ctx.send(reply)


@bot.command()
@checks.game_not_active()
@checks.game_not_paused()
@checks.roles_config()
async def playing(ctx):
    reply = "Set user " + ctx.author.mention + " to "
    if logger.user_set(ctx.author, 'Playing'):
        await ctx.author.add_roles(roles.get_role('playing_role'))
        reply += "playing."
    else:
        await ctx.author.remove_roles(roles.get_role('playing_role'))
        reply += "not playing."
    await ctx.reply(reply)


# Tag commands

@bot.command()
@checks.game_not_active()
@checks.game_not_paused()
async def start(ctx):
    config.cset('active', True)
    config.cset('start_time', logger.log('START'))
    logger.zero_leaderboard()
    await roles.start_roles(ctx.author)
    await ctx.send(roles.get_role('playing_role').mention + "\nGame has started!")


@bot.command()
@checks.game_active()
async def end(ctx):
    config.cset('active', False)
    config.cset('end_time', logger.log('END'))
    await roles.end_roles()
    # logger.user_set_all('Playing', 'False')
    await ctx.send(roles.get_role('playing_role').mention + "\nGame has ended!")


@bot.command()
@checks.game_active()
@checks.game_not_paused()
async def pause(ctx):
    return


@bot.command()
@checks.game_not_active()
@checks.game_paused()
async def resume(ctx):
    return


@bot.command()
@checks.game_active()
@checks.game_not_paused()
@checks.is_playing()
@checks.is_it()
@checks.roles_config()
async def tag(ctx, *, tagged: discord.Member):
    last_log = logger.get_last_log('TAG')
    if last_log is None:
        last_time = config.cget('start_time')
    else:
        last_time = int(last_log)
    it_time = int(time.time()) - last_time
    logger.add_leaderboard(ctx.author, it_time)
    logger.log('TAG', tagged)
    await roles.tag(ctx.author, tagged)
    await ctx.send("@Playing\n" + tagged.mention + " has been tagged by " + ctx.author.mention + ".")


@playing.error
@start.error
@end.error
@tag.error
async def game_error(ctx, error):
    if isinstance(error, checks.RolesFailure):
        await ctx.reply(error)
    elif isinstance(error, commands.CheckFailure):
        await ctx.reply("Oops, you can't do that right now!")
    else:
        await ctx.reply("Oops, something went wrong.")
    if config.cget('debug_mode'):
        await ctx.send(error)


@bot.command(name="leaderboard")
async def _leaderboard(ctx):
    reply = leaderboard.to_string(logger.get_leaderboard())
    await ctx.send(reply)


# Owner and debug commands

@bot.command()
@commands.is_owner()
@checks.is_debug()
async def server_reset(ctx):
    return


@bot.command()
@commands.is_owner()
@checks.is_debug()
@checks.game_not_active()
@checks.game_not_paused()
async def leaderboard_reset(ctx):
    logger.reset('leaderboard')
    await ctx.send('`Leaderboard reset.`')


@bot.command()
@commands.is_owner()
@checks.is_debug()
async def config_dump(ctx):
    cdump = "config.ini\n"
    with open("config.ini", "r") as cfile:
        cdump += cfile.read()
    await ctx.send('```' + cdump[:-73] + '```')


@bot.command()
@commands.is_owner()
@checks.is_debug()
@checks.game_not_active()
@checks.game_not_paused()
async def config_reset(ctx):
    config.reset()
    await ctx.send("```'config.ini' reset.\nWARNING: this command does not reset 'initial_config', "
                   "'guild_settings', or 'bot_token'.```")


@bot.command()
@commands.is_owner()
@checks.is_debug()
@checks.game_not_active()
@checks.game_not_paused()
async def user_reset(ctx):
    logger.reset('users')
    await roles.end_roles()
    playing_role = roles.get_role('playing_role')
    guild = bot.get_guild(config.cget('guild_id'))
    for m in guild.members:
        if playing_role in m.roles:
            await m.remove_roles(playing_role)
    await ctx.send("`Users reset.`")


@bot.command()
@commands.is_owner()
@checks.is_debug()
async def export(ctx):
    await ctx.send(file='logs.db')


@bot.command()
@commands.is_owner()
@checks.is_debug()
async def role(ctx, *, added_role: discord.Role):
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
@user_reset.error
@export.error
@role.error
@toggle_debug.error
async def debug_error(ctx, error):
    if isinstance(error, checks.DebugModeError):
        await ctx.reply(error)
    elif isinstance(error, commands.CheckFailure):
        await ctx.reply("Oops, you can't do that right now!")
    else:
        await ctx.reply("Oops, something went wrong.")
    if config.cget('debug_mode'):
        await ctx.send(error)


# Global checks
@bot.check
async def globally_block_dms(ctx):
    return ctx.guild is not None


bot_token = config.cget('bot_token')
if bot_token != 'NULL':
    bot.run(bot_token)
else:
    print("BOT TOKEN IS MISSING")
