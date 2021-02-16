from os import utime
import random

from time import time
from discord.ext import commands

from lib.embed import construct_embed
from lib.enums import embed_color

from utils.time import format_time_short, seconds_to_time

class Utility(commands.Cog, name="Utility Commands"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    async def help(self, ctx, show_mod: str = None) -> None:
        if show_mod == "mod":
            show_mod = True
        elif show_mod == None:
            show_mod = False
        else:
            return await ctx.send(
                random.choice([
                    "Help what..?",
                    "I can't understand that, sorry.",
                    "I am unable to help you with that.",
                    "Invalid request.",
                    "Unknown request."
                ])
            )

        embed = construct_embed(color=embed_color["DEFAULT"])

        if show_mod:
            embed.title = "Moderator Commands"
            embed.description = """These commands require certain permissions.
            *Should be obvious what sort of permission is required to execute a certain command*"""
        else:
            embed.title = "Commands"
            embed.description = f"""Use `{ctx.prefix}help mod` to see moderator commands."""

        embed.set_thumbnail(url="https://files.catbox.moe/7bzqc2.gif")

        def check_mod_cog(cog):
            if "server" in cog.qualified_name.lower():
                return True
            if "mod" in cog.qualified_name.lower():
                return True

            return False

        for _, cog in self.bot.cogs.items():
            if show_mod:
                if check_mod_cog(cog) == False:
                    continue
            else:
                if check_mod_cog(cog) == True:
                    continue

            if len(cog.get_commands()) == 0:
                continue

            commands = []
            
            for command in cog.walk_commands():
                if command.hidden:
                    continue
                if command.parent != None:
                    continue
                
                commands.append(str(command))

            if (len(commands)) != 0:
                embed.add_field(
                    name=cog.qualified_name,
                    value="```\n{}```".format("\n".join(commands))
                )

        await ctx.send(embed=embed)

    @commands.command()
    async def avatar(self, ctx, member = None):
        member = await self.bot.get_user(ctx, member)
        if member == None:
            return await ctx.send("Unable to find this Member.")

        embed = construct_embed(
            title=f"Avatar of `{member}`",
            description=f"[Download Link]({member.avatar_url_as(format='jpg')})",
            color=embed_color["DEFAULT"]
        )

        embed.set_image(url=member.avatar_url)

        await ctx.send(embed=embed)

    @commands.command()
    async def user(self, ctx, user = None):
        user = await self.bot.get_user(ctx, user)
        if user == None:
            return await ctx.send("Unable to find this User.")

        embed =  construct_embed(
            title=f"User `{user}`",
            color=embed_color["DEFAULT"]
        )

        embed.set_thumbnail(url=user.avatar_url)

        embed.add_field(
            name="Information",
            value=f"""**ID**: {user.id}
            **Bot**: {'Yes' if user.bot else 'No'}
            **Account Created at**: {user.created_at.strftime("%B %d %Y, %H:%M")}
            """,
            inline=False
        )

        if user not in self.bot.users:
            embed.description = "I do not share a server with this user."
        else:
            shared_guilds = []

            for guild in self.bot.guilds:
                for member in guild.members:
                    if user == member:
                        shared_guilds.append(guild)

            embed.add_field(name="Shared Servers", value=", ".join(f'`{str(guild)}`' for guild in shared_guilds))

        await ctx.send(embed=embed)

    @commands.command()
    async def uptime(self, ctx) -> None:
        uptime = seconds_to_time(time() - self.bot.startup_time)

        await ctx.send(
            f"> I've been up for **{format_time_short(uptime)}**."
        )

    @commands.command()
    async def ping(self, ctx) -> None: 
        await ctx.send(f"> It took **{round(await self.bot.get_latency(ctx.channel) * 1000)}ms**.")

def setup(bot):
    bot.add_cog(Utility(bot))