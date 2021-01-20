import sqlite3, os

class DatabaseTool:
    """
    Simple database management tool.

    Parametres:
    - guild: discord.Guild object
    """

    def __init__(self, guild):
        self.guild = guild

        # not sure why I need to do it like this, otherwise errors out because ??
        self.connection = sqlite3.connect(f"{os.getcwd()}/database/{guild.id}.db")
        self.cursor = self.connection.cursor()

    def __del__(self):
        # close connection when object is deleted
        self.connection.close()

    def check_guild(self):
        """
        Checks if the Guild has a table and adds all members.

        If the Guild has a table, only missing members are added.
        """
        
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS members(
            id          INT   NOT NULL,
            messages    INT   NOT NULL,
            warnings    INT   NOT NULL,
            dj_status   INT   NOT NULL
        )""")
        self.connection.commit()

        # also add all members after creating our table
        self.add_all_guild_members()

    def add_all_guild_members(self):
        """Adds all members that aren't in the database yet."""

        for member in self.guild.members:
            # if the member is not in the table
            if len(self.cursor.execute(f"SELECT * FROM members WHERE id={member.id}").fetchall()) == 0:
                # add them
                self.add_guild_member(member)
            else:
                pass

    def add_guild_member(self, member):
        """
        Add a guild member.
        
        Parametres:
        - member: discord.Member object
        """

        self.cursor.execute(f"INSERT INTO members (id,messages,warnings,dj_status) VALUES ({member.id},0,0,0)")
        self.connection.commit()

    def get_member_data(self, member):
        """
        Returns a List of a member's data.
        
        List order: messages, warnings

        Parametres:
        - member: discord.Member object
        """

        messages = self.cursor.execute(f"SELECT messages FROM members WHERE id={member.id}").fetchone()[0]
        warnings = self.cursor.execute(f"SELECT warnings FROM members WHERE id={member.id}").fetchone()[0]
        warnings = self.cursor.execute(f"SELECT dj_status FROM members WHERE id={member.id}").fetchone()[0]

        return [messages, warnings]

    def get_all_members(self):
        """Returns a List of all members' data in a guild."""

        members = []

        for member in self.guild.members:
            if member.bot:
                pass

            members.append([member, self.get_member_data(member)])

        return members


    def update_member_data(self, member, key, value):
        """
        Updates a given member's key with a new value.

        Parametres:
        - member: discord.Member object
        - key: Name of the key we're updating
        - value: The new value of the key
        """
        
        self.cursor.execute(f"UPDATE members SET {key}={value} WHERE id={member.id}")
        self.connection.commit()
