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

def setup(bot):
    bot.add_cog(Events(bot))