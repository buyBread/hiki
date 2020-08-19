import sqlite3, random

# single-guild / global

connection = sqlite3.connect("database.db")
cursor = connection.cursor()

def commit():
    connection.commit()

def add_user(member):
    # if a member's id is not in the table
    if len(cursor.execute(f"SELECT * FROM users WHERE id={member.id}").fetchall()) == 0:
        if member.bot == False:
            # add them
            cursor.execute(f"INSERT INTO users(id, messages, exp, lvl) VALUES({member.id}, {0}, {0}, {1})")
            commit()

def setup_users(members):
    # create a users table if it does not exist
    cursor.execute("CREATE TABLE IF NOT EXISTS users(id integer NOT NULL, messages integer NOT NULL, exp real NOT NULL, lvl integer NOT NULL)")
    
    # add all members to the users table
    for member in members:
        add_user(member)

def get_message_count(member):
    return cursor.execute(f"SELECT messages FROM users WHERE id={member.id}").fetchone()[0]

def get_experience(member):
    return cursor.execute(f"SELECT exp FROM users WHERE id={member.id}").fetchone()[0]

def get_level(member):
    return cursor.execute(f"SELECT lvl FROM users WHERE id={member.id}").fetchone()[0]

def get_top_users(members):
    users = []
    for member in members:
        if member.bot == False:
            users.append([member, (((get_level(member) - 1) * 50) + get_experience(member))])

    users.sort(key=lambda x: x[1], reverse=True)
    return users
    
def update_message_count(member):
    cursor.execute(f"SELECT messages FROM users WHERE id={member.id}")
    cursor.execute(f"UPDATE users SET messages={get_message_count(member) + 1} WHERE id={member.id}")

    commit()

def update_level(member):    
    cursor.execute(f"SELECT exp FROM users WHERE id={member.id}")
    cursor.execute(f"UPDATE users SET exp={get_experience(member) + (random.uniform(1, 3) / (get_level(member) / 2))} WHERE id={member.id}")

    if (get_experience(member) > 50):
        cursor.execute(f"UPDATE users SET exp={get_experience(member) - 50} WHERE id={member.id}")
        cursor.execute(f"UPDATE users SET lvl={get_level(member) + 1} WHERE id={member.id}")

    commit()
