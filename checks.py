from discord.ext import commands
import config
import logger
import time

def game_active():
    async def predicate(ctx):
        active = config.cget('active')
        if not active:
            raise commands.CheckFailure("The game is not active.")
        return True
    return commands.check(predicate)


def game_not_active():
    # there's probably a better way of doing this
    async def predicate(ctx):
        active = config.cget('active')
        if active:
            raise commands.CheckFailure("The game is active.")
        return True
    return commands.check(predicate)


def game_paused():
    async def predicate(ctx):
        paused = config.cget('paused')
        if not paused:
            raise commands.CheckFailure("The game is not paused.")
        return True
    return commands.check(predicate)


def game_not_paused():
    async def predicate(ctx):
        paused = config.cget('paused')
        if paused:
            raise commands.CheckFailure("The game is paused.")
        return True
    return commands.check(predicate)


def game_not_cooldown():
    async def predicate(ctx):
        last_tag = logger.get_last_log('Tag')
        if last_tag is None:
            return True
        is_cooldown = (int(time.time()) - last_tag) < config.cget('cooldown')
        if is_cooldown:
            raise commands.CheckFailure("The game is on cooldown.")
        return True
    return commands.check(predicate)


def is_playing():
    async def predicate(ctx):
        playing = logger.user_check(ctx.author, 'Playing')
        if not playing:
            raise commands.CheckFailure("You are not playing.")
        return True
    return commands.check(predicate)


def is_it():
    async def predicate(ctx):
        it = logger.user_check(ctx.author, 'It')
        if not it:
            raise commands.CheckFailure("You are not it.")
        return True
    return commands.check(predicate)


class DebugModeError(commands.CheckFailure):
    pass

def is_debug():
    async def predicate(ctx):
        if not config.cget('debug_mode'):
            raise DebugModeError("Oops, you can't do that without debug mode.")
        return True
    return commands.check(predicate)


class RolesFailure(commands.CheckFailure):
    pass

def roles_config():
    async def predicate(ctx):
        from roles import get_role
        playing_role = get_role('playing_role') is not None
        it_role = get_role('it_role') is not None
        not_it_role = get_role('not_it_role') is not None
        if not playing_role and it_role and not_it_role:
            raise RolesFailure('`CONFIG ERROR: You are missing one or more role IDs.`')
        return True
    return commands.check(predicate)
