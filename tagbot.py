import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', description="TagBot", help_command=None, intents=intents)


@bot.event
async def on_ready():
    print('Logged in as', bot.user)


# Command Checks


# Config commands

@bot.command()
async def playing(ctx):
    return

# Tag commands

@bot.command()
async def start(ctx):
    return


@bot.command()
async def end(ctx):
    return


@bot.command()
async def pause(ctx):
    return


@bot.command()
async def resume(ctx):
    return


@bot.command()
async def tag(ctx):
    return


@bot.command()
async def leaderboard(ctx):
    return


# Owner and debug commands

@bot.command()
async def server_reset(ctx):
    return


@bot.command()
async def leaderboard_reset(ctx):
    return


@bot.command()
async def config_reset(ctx):
    return


@bot.command()
async def toggle_debug(ctx):
    return


bot.run('INSERT-YOUR-TOKEN-HERE')
