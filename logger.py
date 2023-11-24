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
    query = "SELECT MAX(Timestamp) FROM game_logs WHERE Event = '" + event + "';"
    timestamp = db.execute(query)
    check = timestamp.fetchone()
    if check is None:
        return None
    return check[0]


# user functions

def add_user(user_id):
    check = db.execute("SELECT UserID FROM users WHERE UserID=" + user_id + ";")
    if check.fetchone() is None:
        query = "INSERT INTO users VALUES (" + user_id + ", '<@" + user_id + ">', " + "'False', 'False');"
        db.execute(query)
    check = db.execute("SELECT UserID FROM leaderboard WHERE UserID=" + user_id + ";")
    if check.fetchone() is None:
        query = "INSERT INTO leaderboard VALUES(" + user_id + ", 0);"
        db.execute(query)
    db.commit()


# used to set Playing, It
def user_set(user, row):
    add_user(str(user.id))
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
    cur_val = check.fetchone()
    if cur_val is None or cur_val[0] is None:
        raise TypeError("Query returned None object")
    return True if cur_val[0] == "True" else False

def user_set_all(row, val):
    db.execute("UPDATE users SET " + row + "=" + val + ";")
    db.commit()


# leaderboard functions

def get_leaderboard():
    check = db.execute("SELECT Mention, TotalTime FROM users, leaderboard WHERE users.UserID=leaderboard.UserID AND "
                       "users.Playing = 'True' ORDER BY TotalTime DESC;")
    return check.fetchall()

def add_leaderboard(user, new_time):
    add_user(str(user.id))
    check = db.execute("SELECT TotalTime FROM leaderboard WHERE UserID=" + user.id + ";")
    result = check.fetchone()
    if result is None or result[0] is None:
        old_time = 0
    else:
        old_time = int(result[0])
    query = "UPDATE leaderboard SET TotalTime=" + str(old_time + new_time) + " WHERE UserID=" + str(user.id) + ";"
    db.execute(query)
    db.commit()


def zero_leaderboard():
    query = "UPDATE leaderboard SET TotalTime=0;"
    db.execute(query)
    db.commit()


# debug functions

def reset(table):
    db.execute("DELETE FROM " + table + ";")
    db.commit()
