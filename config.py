import configparser


configP = configparser.ConfigParser()
configP.read('config.ini')
debug_settings = configP['debug_settings']
game_settings = configP['game_settings']
pause_settings = configP['pause_settings']

def update():
    with open('config.ini', 'w') as file:
        configP.write(file)


def get_debug_mode():
    return debug_settings.getboolean('debug_mode')

def get_active():
    return game_settings.getboolean('active')

def get_start_time():
    return game_settings.getint('start_time')

def get_end_time():
    return game_settings.getint('end_time')

def get_cooldown():
    return game_settings.getint('cooldown')

def get_paused():
    return pause_settings.getboolean('paused')

def get_resume_time():
    return pause_settings.getint('resume_time')


def set_debug_mode(val):
    debug_settings['debug_mode'] = str(val)
    update()

def set_active(val):
    game_settings['active'] = str(val)
    update()

def set_start_time(val):
    game_settings['start_time'] = str(val)
    update()

def set_end_time(val):
    game_settings['end_time'] = str(val)
    update()

def set_cooldown(val):
    game_settings['cooldown'] = str(val)
    update()

def set_paused(val):
    pause_settings['paused'] = str(val)
    update()

def set_resume_time(val):
    pause_settings['resume_time'] = str(val)
    update()


