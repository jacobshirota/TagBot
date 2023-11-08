import sqlite3
import discord
import config
import time

db = sqlite3.connect("logs.db")

if config.cget('initial_config'):
    db.execute("SOURCE init.sql")
    config.cset('initial_config', 'False')


def log(*args):
    query = "INSERT INTO game_logs VALUES (" + config.cget('start_time')
    match args[0]:
        case 'start':
            # add case for immediate start
            query += ", 'START', NULL, "
        case 'end':
            query += ", 'END', NULL, "
        case 'pause':
            query += ", 'PAUSE', NULL, "
        case 'resume':
            query += ", 'RESUME', NULL, "
        case 'tag':
            query += ", 'TAG', " + args[1] + ", "
    query += str(int(time.time())) + ");"
    db.execute(query)


# ADD add_user(user)


