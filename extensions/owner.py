import discord, requests
from discord.ext import commands
from utils import cosmetic

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

    @commands.group()
    async def change(self, ctx):
        pass

    @change.command(name="username")
    async def change_username(self, ctx, *, username: str):
        await self.bot.user.edit(username=username)

    @change.command(name="presence")
    async def change_presence(self, ctx, type: str, *, text: str):
        await cosmetic.change_presence(self.bot, type, text)

    @change.command(name="avatar")
    async def change_avatar(self, ctx, url: str = None):
        if url == None:
            if len(ctx.message.attachments) == 1:
                url = ctx.message.attachments[0].url

        # probably not the most cleanest way, but it works so ¯\_(ツ)_/¯
        try:
            with open("/tmp/bot_avatar.jpg", "wb") as f:
                f.write(requests.get(url).content)            
            with open("/tmp/bot_avatar.jpg", "rb") as f:
                await self.bot.user.edit(avatar=bytearray(f.read()))
        # improper, fix later
        except:
            await ctx.send("Provide a URL or attachment.")
            return

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

class CogManagement(commands.Cog, command_attrs=dict(hidden=True)):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="cogs")
    async def cogs_utility(self, ctx):
        pass        

    # hard codeded pls fix me
    # hard codeded pls fix me
    # hard codeded pls fix me
    @cogs_utility.command(name="list")
    async def cogs_list(self, ctx):    
        from extensions import events, owner, server, utility

        embed = discord.Embed(title="Cogs List")
        embed.color = 0x2F3136

        cogs = []
        for cog in self.bot.cogs:
            cog = self.bot.get_cog(cog)
            cogs.append(str(cog))

        events_cogs = []
        owner_cogs = []
        server_cogs = []
        utility_cogs = []

        for cog in cogs:
            for obj in dir(events):
                if obj == "db":
                    pass
                if obj in cog:
                    events_cogs.append(obj)
            for obj in dir(owner):
                if obj in cog:
                    owner_cogs.append(obj)
            for obj in dir(server):
                if obj in cog:
                    server_cogs.append(obj)
            for obj in dir(utility):
                if obj == "db":
                    pass
                if obj in cog:
                    utility_cogs.append(obj)

        if events_cogs != []:
            embed.add_field(name="events.py", value="\n".join(cog for cog in events_cogs), inline=True)
        if owner_cogs != []:
            embed.add_field(name="owner.py", value="\n".join(cog for cog in owner_cogs), inline=True)
        if server_cogs != []:
            embed.add_field(name="server.py", value="\n".join(cog for cog in server_cogs), inline=True)
        if utility_cogs != []:
            embed.add_field(name="utility.py", value="\n".join(cog for cog in utility_cogs), inline=True)

        await ctx.send(embed=embed)

    @cogs_utility.command(name="load")
    async def cogs_load(self, ctx, *, extension: str):
        self.bot.load_extension(f"extensions.{extension}")

    @cogs_utility.command(name="unload")
    async def cogs_unload(self, ctx, *, extension: str):
        self.bot.unload_extension(f"extensions.{extension}")

    @cogs_utility.command(name="reload")
    async def cogs_reload(self, ctx, *, extension: str):
        self.bot.reload_extension(f"extensions.{extension}")

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