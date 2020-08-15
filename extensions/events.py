from utils import database as db
from utils.cosmetic import change_presence
from utils.messaging import formatter
from discord.ext import commands

class GeneralEvents(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Ready!", end = "\n\n")
        await change_presence(self.bot, "listening", "Subwoofer Lullaby")

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

        old_level = db.get_level(author)
        db.update_user(author)
        new_level = db.get_level(author)

        if (old_level < new_level):
            await message.channel.send(formatter(f"{author.mention} **{new_level}**!").qoute())

class ErrorHandling(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        error = getattr(error, 'original', error)

        if isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(formatter(f"{formatter(error.param.name).block()} is missing\n").qoute())
        else:
            await ctx.send(formatter(f"Something went wrong.. {formatter(error).codeblock()}").qoute())

import asyncio # for sleeping certain events
from discord import AuditLogAction

# relays audit log information + custom events
class AuditLog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # todo:
    # - log bans
    # - log kicks
    # - log message edits
    # - log message deletes
    # - log message deletes in bulk:
    #   -> upon running clear send every message that has been deleted
    # - log commands
    # - log command errors 

def setup(bot):
    bot.add_cog(GeneralEvents(bot))
    bot.add_cog(ErrorHandling(bot))
    bot.add_cog(AuditLog(bot))
