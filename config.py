import configparser


configP = configparser.ConfigParser()
configP.read('config.ini')
debug_settings = configP['debug_settings']
game_settings = configP['game_settings']
pause_settings = configP['pause_settings']
guild_settings = configP['guild_settings']


def update():
    with open('config.ini', 'w') as file:
        configP.write(file)


def cget(arg):
    if arg in ['debug_mode', 'initial_config']:
        return debug_settings.getboolean(arg)
    elif arg == 'active':
        return game_settings.getboolean(arg)
    elif arg in ['start_time', 'end_time', 'cooldown']:
        return game_settings.getint(arg)
    elif arg == 'paused':
        return pause_settings.getboolean(arg)
    elif arg == 'resume_time':
        return pause_settings.getint(arg)
    elif arg in ['guild_id', 'playing_role', 'it_role', 'not_it_role']:
        if guild_settings[arg] == 'NULL':
            return None
        else:
            return guild_settings.getint(arg)


def cset(*args):
    if args[0] in ['debug_mode', 'initial_config']:
        debug_settings[args[0]] = str(args[1])
    elif args[0] in ['active', 'start_time', 'end_time', 'cooldown']:
        game_settings[args[0]] = str(args[1])
    elif args[0] in ['paused', 'resume_time']:
        pause_settings[args[0]] = str(args[1])
    update()


