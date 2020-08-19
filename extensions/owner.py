import requests
from utils.cosmetic import change_presence
from discord.ext import commands

class BotProfile(commands.Cog, command_attrs=dict(hidden=True)):

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def change(self, ctx):
        pass

    @change.command(name="username")
    async def change_username(self, ctx, *, username: str):
        await self.bot.user.edit(username=username)

    @change.command(name="presence")
    async def change_presence(self, ctx, type: str, *, text: str):
        await change_presence(self.bot, type, text)

    @change.command(name="avatar")
    async def change_avatar(self, ctx, url: str = None):
        if url == None:
            if len(ctx.message.attachments) == 1:
                url = ctx.message.attachments[0].url

        image = None
        try:
            with open("/tmp/bot_avatar.jpg", "wb") as f:
                f.write(requests.get(url).content)            
            with open("/tmp/bot_avatar.jpg", "rb") as f:
                image = bytearray(f.read())
        except:
            await ctx.send("Provide a URL or attachment.")
            return

        await self.bot.user.edit(avatar=image)

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