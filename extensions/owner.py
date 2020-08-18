from discord.ext import commands

class BotProfile(commands.Cog, command_attrs=dict(hidden=True)):

    def __init__(self, bot):
        self.bot = bot

    # todo:
    # - add name change
    # - add avatar change
    # - add presence change

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

class CogManagement(commands.Cog, command_attrs=dict(hidden=True)):

    def __init__(self, bot):
        self.bot = bot

    # todo:
    # - add cog list
    # - add cog loading
    # - add cog unloading
    # - add cog reloading

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)  

class DatabaseManagement(commands.Cog, command_attrs=dict(hidden=True)):

    def __init__(self, bot):
        self.bot = bot

    # todo:
    # - add database reset
    # - add database value modification

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)  

def setup(bot):
    bot.add_cog(BotProfile(bot))
    bot.add_cog(CogManagement(bot))