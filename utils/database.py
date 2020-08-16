import sqlite3
from random import uniform

# todo: make sure to make the database per guild based.
#       just in case.

connection = sqlite3.connect("database.db")
cursor = connection.cursor()

def commit():
    connection.commit()

def add_user(member):
    # if a member's id is not in the table
    if len(cursor.execute("SELECT * FROM users WHERE id=?", (member.id, )).fetchall()) == 0:
        # add them
        cursor.execute("INSERT INTO users(id, messages, exp, lvl) VALUES(?, ?, ?, ?)", (member.id, 0, 0, 1))
        commit()

def setup_users(members):
    # create a users table if it does not exist
    cursor.execute("CREATE TABLE IF NOT EXISTS users(id integer NOT NULL, messages integer NOT NULL, exp real NOT NULL, lvl integer NOT NULL)")
    
    # add all members to the users table
    for member in members:
        if member.bot:
            pass # don't add bots to the database

        add_user(member)

    commit()

def get_message_count(member):
    return cursor.execute(f"SELECT messages FROM users WHERE id={member.id}").fetchone()[0]

def get_experience(member):
    return cursor.execute(f"SELECT exp FROM users WHERE id={member.id}").fetchone()[0]

def get_level(member):
    return cursor.execute(f"SELECT lvl FROM users WHERE id={member.id}").fetchone()[0]

def update_user(member):
    cursor.execute(f"SELECT messages FROM users WHERE id={member.id}")
    cursor.execute(f"UPDATE users SET messages={get_message_count(member) + 1} WHERE id={member.id}")
    
    cursor.execute(f"SELECT exp FROM users WHERE id={member.id}")
    cursor.execute(f"UPDATE users SET exp={get_experience(member) + (uniform(2, 12) / get_level(member) / 2)} WHERE id={member.id}")

    if (get_experience(member) > 50):
        cursor.execute(f"UPDATE users SET exp={get_experience(member) - 50} WHERE id={member.id}")
        cursor.execute(f"UPDATE users SET lvl={get_level(member) + 1} WHERE id={member.id}")

    commit()
