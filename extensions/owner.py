import discord, requests, os, importlib
from discord.ext import commands
from utils import cosmetic
from utils.messaging import formatter

class GeneralOwner(commands.Cog, command_attrs=dict(hidden=True)):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def say(self, ctx, *, msg):
        await ctx.send(msg)

    @commands.command()
    async def esay(self, ctx, title, msg):
        await ctx.send(embed=discord.Embed(title=title, description=msg, color=0x2F3136))

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

class BotProfile(commands.Cog, command_attrs=dict(hidden=True)):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=["bot", "change", "change bot", "bot change"])
    async def _bot_profile(self, ctx):
        if ctx.invoked_subcommand == None:
            embed = discord.Embed(title="Available Commands")
            embed.color = 0x2F3136
            embed.description = "\n".join(formatter(str(x)).block() for x in ctx.command.commands)
            await ctx.send(embed=embed)

    @_bot_profile.command(name="username")
    async def change_username(self, ctx, *, username: str):
        await self.bot.user.edit(username=username)
        await ctx.send(f"Changed username to {username}.")

    @_bot_profile.command(name="presence")
    async def change_presence(self, ctx, type: str, *, text: str):
        await cosmetic.change_presence(self.bot, type, text)
        await ctx.send(f"Changed presence to {text}.")

    @_bot_profile.command(name="avatar")
    async def change_avatar(self, ctx, url: str = None):
        if url == None:
            if len(ctx.message.attachments) == 1:
                url = ctx.message.attachments[0].url

        # probably not the most cleanest way, but it works so ¯\_(ツ)_/¯
        if url != None:
            try:
                with open("/tmp/bot_avatar.jpg", "wb") as f:
                    f.write(requests.get(url).content)            
                with open("/tmp/bot_avatar.jpg", "rb") as f:
                    await self.bot.user.edit(avatar=bytearray(f.read()))
                    await ctx.send("Changed avatar.")
            except:
                await ctx.send("Failed retrieving the image.")
        else:
            await ctx.send("Provide an image or a URL.")

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

class CogManagement(commands.Cog, command_attrs=dict(hidden=True)):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="cogs")
    async def cogs_utility(self, ctx):
        if ctx.invoked_subcommand == None:
            embed = discord.Embed(title="Available Commands")
            embed.color = 0x2F3136
            embed.description = "\n".join(formatter(str(x)).block() for x in ctx.command.commands)
            await ctx.send(embed=embed)

    @cogs_utility.command(name="list")
    async def cogs_list(self, ctx): 
        extensions = [] 
        for extension in os.listdir("extensions"):
            extensions.append(f"extensions.{extension[:-3]}")

        cogs = []
        for cog in self.bot.cogs:
            cogs.append(cog)

        embed = discord.Embed(title="Cogs List")
        embed.color = 0x2F3136

        for extension in extensions:
            globals()["ext"] = importlib.import_module(extension)
            value = ""

            for cog in cogs:
                for obj in dir(ext):
                    if cog == obj:
                        value += f"{cog}\n"
            
            if value == "":
                pass
            else:
                embed.add_field(name=extension.split(".")[1] + ".py", value=value, inline=True)

        await ctx.send(embed=embed)

    @cogs_utility.command(name="load")
    async def cogs_load(self, ctx, *, extension: str):
        self.bot.load_extension(f"extensions.{extension}")
        await ctx.send(f"Loaded **{extension}.py**")

    @cogs_utility.command(name="unload")
    async def cogs_unload(self, ctx, *, extension: str):
        self.bot.unload_extension(f"extensions.{extension}")
        await ctx.send(f"Unloaded **{extension}.**")

    @cogs_utility.command(name="reload")
    async def cogs_reload(self, ctx, *, extension: str):
        self.bot.reload_extension(f"extensions.{extension}")
        await ctx.send(f"Reloaded **{extension}.py**")

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)  

class DatabaseManagement(commands.Cog, command_attrs=dict(hidden=True)):

    def __init__(self, bot):
        self.bot = bot

    # todo:
    # - add guild database reset
    # - add guild database value modification

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)  

def setup(bot):
    bot.add_cog(GeneralOwner(bot))
    bot.add_cog(BotProfile(bot))
    bot.add_cog(CogManagement(bot))
    bot.add_cog(DatabaseManagement(bot))