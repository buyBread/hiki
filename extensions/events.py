from utils import database as db
from discord.ext import commands

class Events(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Ready!", end = "\n\n")

        db.setup_users(self.bot, self.bot.get_all_members())

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.id == self.bot.user.id:
            return

        db.add_user(member)

    @commands.Cog.listener()
    async def on_message(self, message):
        author = message.author

        if author.id == self.bot.user.id:
            return

        db.add_message(author)
        print("I've seen {0} send {1} messages".format(author, db.cursor.execute('SELECT messages FROM users WHERE id=?', (author.id, )).fetchall()[0][0]))

def setup(bot):
    bot.add_cog(Events(bot))