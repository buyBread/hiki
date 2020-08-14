import sqlite3
from discord.ext import commands

class Events(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.db = sqlite3.connect('database.db')
        self.cs = self.db.cursor()

    @commands.Cog.listener()
    async def on_ready(self):
        print("on_ready")

        self.cs.execute("CREATE TABLE IF NOT EXISTS users(id integer NOT NULL, messages integer NOT NULL)")
        for member in self.bot.get_all_members():
            if member.id == self.bot.user.id:
                return

            if len(self.cs.execute('SELECT * FROM users WHERE id=?', (member.id, )).fetchall()) == 0:
                self.cs.execute('INSERT INTO users(id, messages) VALUES(?, ?)', (member.id, 0))
                self.db.commit()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.id == self.bot.user.id:
                return

        if len(self.cs.execute('SELECT * FROM users WHERE id=?', (member.id, )).fetchall()) == 0:
            self.cs.execute('INSERT INTO users(id, messages) VALUES(?, ?)', (member.id, 0))
            self.db.commit()

    @commands.Cog.listener()
    async def on_message(self, message):
        author = message.author

        if author.id == self.bot.user.id:
            return

        self.cs.execute('UPDATE users SET messages=? + ? WHERE id=?', (self.cs.execute('SELECT messages FROM users WHERE id=?', (author.id, )).fetchall()[0][0], 1, author.id))
        self.db.commit()

def setup(bot):
    bot.add_cog(Events(bot))