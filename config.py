import configparser


configP = configparser.ConfigParser()
configP.read('config.ini')
debug_settings = configP['debug_settings']
game_settings = configP['game_settings']
pause_settings = configP['pause_settings']


def update():
    with open('config.ini', 'w') as file:
        configP.write(file)


def cget(arg):
    match arg:
        case 'debug_mode' | 'initial_config':
            return debug_settings.getboolean(arg)
        case 'active':
            return game_settings.getboolean(arg)
        case 'start_time' | 'end_time' | 'cooldown':
            return game_settings.getint(arg)
        case 'paused':
            return pause_settings.getboolean(arg)
        case 'resume_time':
            return pause_settings.getint(arg)


def cset(*args):
    match args[0]:
        case 'debug_mode' | 'initial_config':
            debug_settings[args[0]] = str(args[1])
        case 'active' | 'start_time' | 'end_time' | 'cooldown':
            game_settings[args[0]] = str(args[1])
        case 'paused' | 'resume_time':
            pause_settings[args[0]] = str(args[1])
    update()


