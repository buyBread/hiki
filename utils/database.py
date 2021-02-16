import discord
import sqlite3
import os

class GlobalDatabase:
    """
    Discord Bot global database management.

    Parameters:
        
        guilds: the List of every discord.Guild the Bot is a part of
    """

    def __init__(self, guilds):
        # not sure why I need to use os.getcwd(), otherwise errors out because ??
        self.connection = sqlite3.connect(f"{os.getcwd()}/database/global.db")
        self.cursor = self.connection.cursor()
        
        self.guilds = guilds

    def __del__(self):
        # close connection when object is deleted
        self.connection.close()

    def initialize(self) -> None:
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS members(
            id            INT             NOT NULL,
            exp           REAL            NOT NULL,
            level         INT             NOT NULL,
            reputation    INT             NOT NULL,
            last_rep      REAL            NOT NULL,
            emoji         CHAR(64),
            color         CHAR(16),
            description   VARCHAR(1024)
        )""")
        self.connection.commit()       

        for guild in self.guilds:
            for member in guild.members:
                if member.bot:
                    continue

                if self.check_member(member) == False:
                    self.add_member(member)

    def check_member(self, member) -> bool:
        # check if member's ID is in the table
        if len(self.cursor.execute(f"SELECT * FROM members WHERE id={member.id}").fetchall()) == 0:
            return False

        return True

    def add_member(self, member) -> None:
        self.cursor.execute(f"INSERT INTO members (id,exp,level,reputation,last_rep,emoji,color,description) VALUES ({member.id},0,1,0,'','','DEFAULT','')")
        self.connection.commit()

    def get_member_data(self, member) -> dict:
        return {
            "EXP": self.cursor.execute(f"SELECT exp FROM members WHERE id={member.id}").fetchone()[0],
            "LEVEL": self.cursor.execute(f"SELECT level FROM members WHERE id={member.id}").fetchone()[0],
            "REPUTATION": self.cursor.execute(f"SELECT reputation FROM members WHERE id={member.id}").fetchone()[0],
            "LAST_REP": self.cursor.execute(f"SELECT last_rep FROM members WHERE id={member.id}").fetchone()[0],
            "EMOJI": self.cursor.execute(f"SELECT emoji FROM members WHERE id={member.id}").fetchone()[0],
            "COLOR": self.cursor.execute(f"SELECT color FROM members WHERE id={member.id}").fetchone()[0],
            "DESCRIPTION": self.cursor.execute(f"SELECT description FROM members WHERE id={member.id}").fetchone()[0],
        }

    def update_member_data(self, member, key, value) -> None:        
        self.cursor.execute(f"UPDATE members SET {key}={value} WHERE id={member.id}")
        self.connection.commit()

class GuildDatabase:
    """
    Discord Bot guild database management.

    Parameters:

        guild: discord.Guild object
    """

    def __init__(self, guild):
        # ditto: GlobalDatabase -> __init__
        self.connection = sqlite3.connect(f"{os.getcwd()}/database/{guild.id}.db")
        self.cursor = self.connection.cursor()

        self.guild = guild

    def __del__(self):
        # close connection when object is deleted
        self.connection.close()

    def initialize(self) -> None:
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS members(
            id          INT       NOT NULL,
            exp         REAL      NOT NULL,
            warnings    INT       NOT NULL,
            dj_status   TINYINT   NOT NULL
        )""")
        self.connection.commit()

        for member in self.guild.members:
            if member.bot:
                continue

            if self.check_member(member) == False:
                self.add_member(member)

    def check_member(self, member) -> bool:
        # check if member's ID is in the table
        if len(self.cursor.execute(f"SELECT * FROM members WHERE id={member.id}").fetchall()) == 0:
            return False

        return True

    def add_member(self, member) -> None:
        self.cursor.execute(f"INSERT INTO members (id,exp,warnings,dj_status) VALUES ({member.id},0,0,0)")
        self.connection.commit()

    def get_member_data(self, member) -> dict:
        return {
            "EXP": self.cursor.execute(f"SELECT exp FROM members WHERE id={member.id}").fetchone()[0],
            "WARNINGS": self.cursor.execute(f"SELECT warnings FROM members WHERE id={member.id}").fetchone()[0],
            "DJ_STATUS": self.cursor.execute(f"SELECT dj_status FROM members WHERE id={member.id}").fetchone()[0]
        }

    def get_all_members(self) -> list:
        members = []

        for member in self.guild.members:
            if member.bot:
                continue

            members.append([member, self.get_member_data(member)])

        return members

    def update_member_data(self, member, key, value) -> None:        
        self.cursor.execute(f"UPDATE members SET {key}={value} WHERE id={member.id}")
        self.connection.commit()
