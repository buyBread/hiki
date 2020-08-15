import sqlite3

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
        cursor.execute("INSERT INTO users(id, messages) VALUES(?, ?)", (member.id, 0))
        commit()

def setup_users(bot, members):
    # create a users table if it does not exist
    cursor.execute("CREATE TABLE IF NOT EXISTS users(id integer NOT NULL, messages integer NOT NULL)")
    
    # add all members to the users table
    for member in members:
        if member.id == bot.user.id:
            return

        add_user(member)

def update_message_count(member):
    cursor.execute("UPDATE users SET messages=? + ? WHERE id=?", (cursor.execute("SELECT messages FROM users WHERE id=?", (member.id, )).fetchall()[0][0], 1, member.id))
    commit()

def get_message_count(member):
    return cursor.execute("SELECT messages FROM users WHERE id=?", (member.id, )).fetchall()[0][0]