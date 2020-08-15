from utils import database as db
from utils.messaging import formatter
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

        db.update_message_count(author)

class ErrorHandling(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        error = getattr(error, "original", error)

        if isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                formatter(f"{formatter(error.param.name).block()} is missing\n"
                            "Run the help command to see required arguments.").qoute()
                )
        else:
            # todo: send to #command-error channel
            await ctx.send(formatter(f"Something went wrong.. {formatter(error).codeblock()}").qoute)

def setup(bot):
    bot.add_cog(Events(bot))
    bot.add_cog(ErrorHandling(bot))