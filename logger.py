import sqlite3
import discord
import config
import time

"""
notes to self: 
add_user doesn't need sanitizing because user.id and user.mention are already in fixed formats. 
user.mention is just "<@[user.id]>", can probably be removed
"""


db = sqlite3.connect("logs.db")

if config.cget('initial_config'):
    with open("init.sql", "r") as sql_file:
        sql_script = sql_file.read()
    cursor = db.cursor()
    cursor.executescript(sql_script)
    db.commit()
    config.cset('initial_config', 'False')


# game_logs functions

def log(*args):
    timestamp = int(time.time())
    query = "INSERT INTO game_logs VALUES (" + str(timestamp) + ", " + str(config.cget('start_time'))
    if args[0] in ['START', 'END', 'PAUSE', 'RESUME']:
        query += ", '" + args[0] + "', NULL);"
    elif args[0] == 'TAG':
        query += ", 'TAG', " + args[1] + ");"
    db.execute(query)
    db.commit()
    return timestamp

def get_last_log(event):
    query = "SELECT MAX(Timestamp) FROM game_logs WHERE Event = " + event + ";"
    timestamp = db.execute(query)
    db.commit()
    return timestamp.fetchone()


# user functions
def add_user(user):
    check = db.execute("SELECT UserID FROM users WHERE UserID=" + str(user.id) + ";")
    if check.fetchone() is not None:
        return False
    query = "INSERT INTO users VALUES (" + str(user.id) + ", '" + user.mention + "', " + "'False', 'False');"
    db.execute(query)
    query = "INSERT INTO leaderboard VALUES(" + str(user.id) + ", 0);"
    db.execute(query)
    db.commit()
    return True

# used to set Playing, It
def user_set(user, row):
    add_user(user)
    check = db.execute("SELECT " + row + " FROM users WHERE UserID=" + str(user.id) + ";")
    old_val = check.fetchone()
    if old_val is None:
        raise TypeError("Query returned None object")
    query = "UPDATE users SET " + row + "="
    query += "'True'" if old_val[0] == "False" else "'False'"
    query += "WHERE UserID=" + str(user.id) + ";"
    db.execute(query)
    db.commit()
    return True if old_val[0] == "False" else False

def user_check(user, row):
    check = db.execute("SELECT " + row + " FROM users WHERE UserID=" + str(user.id) + ";")
    if check.fetchone() is None:
        return False
    return True if check.fetchone()[0] == "'True'" else False

def user_set_all(row, val):
    db.execute("UPDATE users SET " + row + "=" + val + ";")
    db.commit()


# leaderboard functions
def get_leaderboard():
    check = db.execute("SELECT Mention, TotalTime FROM user, leaderboard;")
    return check.fetchall()


# debug functions
def user_reset():
    db.execute("DELETE FROM users;")
    db.commit()