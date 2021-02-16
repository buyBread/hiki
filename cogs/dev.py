import discord
import requests
import os
import importlib

from discord.ext import commands

from lib.embed import construct_embed
from lib.presence import construct_activity
from lib.enums import activity_type, embed_color

from utils.database import GlobalDatabase, GuildDatabase

class GeneralOwner(commands.Cog, command_attrs=dict(hidden=True)):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def say(self, ctx, *, msg) -> None:
        await ctx.send(msg)

    @commands.command()
    async def esay(self, ctx, title, msg) -> None:
        await ctx.send(embed=construct_embed(title=title, description=msg, color=0x2F3136))

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

class BotProfile(commands.Cog, command_attrs=dict(hidden=True)):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=["bot", "change", "change bot", "bot change"])
    async def _bot_profile(self, ctx) -> None:
        if ctx.invoked_subcommand == None:
            embed = construct_embed(title="Available Commands")
            embed.color = embed_color["DEFAULT"]
            embed.description = "\n".join(f"`{str(x)}`" for x in ctx.command.commands)
            await ctx.send(embed=embed)

    @_bot_profile.command(name="username")
    async def change_username(self, ctx, *, username: str) -> None:
        await self.bot.user.edit(username=username)
        await ctx.send(f"Changed username to {username}.")

    @_bot_profile.command(name="presence")
    async def change_presence(self, ctx, type: str, *, text: str) -> None:
        self.bot.change_presence(
            activity=construct_activity(
                type=activity_type[type.upper()],
                name=text
            )
        )
        await ctx.send(f"Changed presence to {type} {text}.")

    @_bot_profile.command(name="avatar")
    async def change_avatar(self, ctx, url: str = None) -> None:
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
    async def cogs_utility(self, ctx) -> None:
        if ctx.invoked_subcommand == None:
            embed = construct_embed(title="Available Commands")
            embed.color = embed_color["DEFAULT"]
            embed.description = "\n".join(f"`{str(x)}`" for x in ctx.command.commands)
            await ctx.send(embed=embed)

    @cogs_utility.command(name="list")
    async def cogs_list(self, ctx) -> None:
        cogs = []
        for cog in os.listdir("cogs"):
            cogs.append(cog)
        
        loaded_cogs = []
        for _, cog in self.bot.cogs.items():
            loaded_cogs.append(cog.qualified_name)
 
        embed = construct_embed(title="Cogs List", color=embed_color["DEFAULT"])

        for cog in cogs:
            cog = f"cogs.{cog[:-3]}"
            globals()["ext"] = importlib.import_module(cog)

            for i in range(0, len(loaded_cogs)):
                for obj in dir(ext):
                    if loaded_cogs[i] == obj:
                        loaded_cogs[i] = f"`{loaded_cogs[i]} ({cog.split('.')[1] + '.py'})`"

        for i in range(0, len(cogs)):
            cogs[i] = f"`{cogs[i]}`"

        embed.add_field(name="All Cogs", value="\n".join(cog for cog in cogs))
        embed.add_field(name="Loaded Cogs", value="\n".join(cog for cog in loaded_cogs))

        await ctx.send(embed=embed)

    @cogs_utility.command(name="load")
    async def cogs_load(self, ctx, *, cog: str) -> None:
        self.bot.load_extension(f"cogs.{cog}")
        await ctx.send(f"Loaded **{cog}.py**")

    @cogs_utility.command(name="unload")
    async def cogs_unload(self, ctx, *, cog: str) -> None:
        self.bot.unload_extension(f"cogs.{cog}")
        await ctx.send(f"Unloaded **{cog}.py**")

    @cogs_utility.command(name="reload")
    async def cogs_reload(self, ctx, *, cog: str) -> None:
        self.bot.reload_extension(f"cogs.{cog}")
        await ctx.send(f"Reloaded **{cog}.py**")

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)  

class DatabaseManagement(commands.Cog, command_attrs=dict(hidden=True)):

    def __init__(self, bot):
        self.bot = bot

    # todo:
    # - global database management

    @commands.group()
    async def database(self, ctx) -> None:
         if ctx.invoked_subcommand == None:
            embed = construct_embed(title="Available Commands")
            embed.color = embed_color["DEFAULT"]
            embed.description = "\n".join(f"`{str(x)}`" for x in ctx.command.commands)
            await ctx.send(embed=embed)

    @database.command(name="search")
    async def database_search(self, ctx, guild = None) -> None:
        database_list = []

        for database in os.listdir("database"):
            database_list.append(database[:-3])

        embed = construct_embed(title="Search results", color=embed_color["DEFAULT"])

        found = False

        # database names are guild IDs
        if guild in database_list:
            found = True
            
            guild = self.bot.get_guild(int(guild))
            
            embed.set_thumbnail(url=guild.icon_url)
            embed.add_field(
                name=guild.name,
                value=f"**Member Count**: {len(guild.members)}",
                inline=True
            )
        else:
            matching_guilds = []

            for x in database_list:
                x = self.bot.get_guild(int(x))

                if guild in x.name:
                    matching_guilds.append(x)

            if len(matching_guilds) > 0:
                found = True

                for x in matching_guilds:
                    if len(matching_guilds) == 1:
                        embed.set_thumbnail(url=x.icon_url)

                    embed.add_field(
                        name=x.name,
                        value=f"**Member Count**: {len(x.members)}\n**ID**: {x.id}",
                        inline=True
                    )
            
        if not found:
            embed.description = "Nothing found."

        await ctx.send(embed=embed)

    @database.command(name="reset")
    async def database_reset(self, ctx, guild) -> None:
        if os.path.exists(f"database/{guild}.db"):
            os.remove(f"database/{guild}.db")

            guild = self.bot.get_guild(int(guild))
            GuildDatabase(guild).initialize()

            await ctx.send(f"Database for guild **{guild.name}** has been reset.")

    @database.command(name="edit")
    async def database_edit(self, ctx, guild, member: discord.Member, key, value) -> None:
        if os.path.exists(f"database/{guild}.db"):
            guild = self.bot.get_guild(int(guild))
            GuildDatabase(guild).update_member_data(member, key, value)

            await ctx.send(f"Database edited for **{guild.name}** guild's member <@{member.id}>.")

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)  

def setup(bot):
    bot.add_cog(GeneralOwner(bot))
    bot.add_cog(BotProfile(bot))
    bot.add_cog(CogManagement(bot))
    bot.add_cog(DatabaseManagement(bot))