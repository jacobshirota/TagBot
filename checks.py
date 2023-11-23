from discord.ext import commands
import config
import logger
import time

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
        if last_tag is None:
            return False
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
