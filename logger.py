import sqlite3
import discord
import config
import time

db = sqlite3.connect("logs.db")

if config.cget('initial_config'):
    db.execute(".read init.sql")
    config.cset('initial_config', 'False')


def log(*args):
    query = "INSERT INTO game_logs VALUES (" + config.cget('start_time')
    if args[0] in ['START', 'END', 'PAUSE', 'RESUME']:
        # add case for immediate start
        query += ", '" + args[0] + "', NULL, "
    elif args[0] == 'TAG':
        query += ", 'TAG', " + args[1] + ", "
    query += str(int(time.time())) + ");"
    db.execute(query)


# ADD add_user(user)


