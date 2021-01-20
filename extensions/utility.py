import discord, asyncio
from discord.ext import commands
from utils.database import DatabaseTool
from utils.messaging import formatter
from datetime import datetime

class UserUtility(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(usage="member")
    async def avatar(self, ctx, *, member: discord.Member=None):
        """Get a Member's profile picture."""
        if member == None:
            member = ctx.author

        embed = discord.Embed(
            title=f"Avatar of {member}",
            description=f"[Click here]({member.avatar_url_as(format='jpeg')}) for the link.",
            timestamp=datetime.utcnow()
        )
        embed.color = 0x2F3136
        embed.set_image(url=member.avatar_url_as(format="jpeg"))

        await ctx.send(embed=embed)

    @commands.command(usage="member")
    async def profile(self, ctx, *, member: discord.Member=None):
        """Display a Member's profile."""
        await asyncio.sleep(1) # let the database catch up

        if member == None:
            member = ctx.author

        if member.bot:
            await ctx.send("Bot's don't have profiles.. :(")
            return

        member_data = DatabaseTool(member.guild).get_member_data(member)

        embed = discord.Embed(
            title=f"Profile of {member}",
            description=
            f"I've seen **{member_data[0]}** messages sent by **{member.name}**.\n"
            f"Level: **{int(member_data[0] / 100) + 1}**\n"
            f"Warnings: **{member_data[1]}**",
            timestamp=datetime.utcnow()
        )
        embed.color = 0x2F3136
        embed.set_thumbnail(url=member.avatar_url)

        await ctx.send(embed=embed)

    @commands.command(aliases=["leaderboard"])
    async def top(self, ctx):
        """Displays the Top 10 members in the server."""
        await asyncio.sleep(0.6) # let the database catch up
        
        embed = discord.Embed(title="Top 10 members", timestamp=datetime.utcnow())
        embed.color = 0x2F3136

        all_member_data = DatabaseTool(ctx.guild).get_all_members()
        # sort data based on member_data[0] (message count)
        all_member_data.sort(key=lambda x: x[1][0], reverse=True)

        description = ""
        for i in range(0, 10):
            member_data = all_member_data[i]
            description += f"{i + 1}. **{member_data[0]}** (Messages: **{member_data[1][0]}**\n"

        embed.description = description

        await ctx.send(embed=embed)

    @commands.command(usage="command")
    async def help(self, ctx, cmd = None):
        """Displays and shows usage of available commands."""
        if cmd == None:       
            embed = discord.Embed(
                title="Help Page",
                description=
                "This is a list of available commands.\n"
                f"Use `{ctx.prefix}help [command]` to see it's usage."   
            )
            embed.color = 0x2F3136

            commands = []

            general_commands = ["\n"]
            mod_commands = ["\n"]
            music_commands = ["\n"]

            for string, cog in self.bot.cogs.items():
                for command in cog.walk_commands():
                    if command.hidden == True:
                        pass
                    elif command in commands:
                        pass
                    elif command.parent != None:
                        pass
                    else:
                        commands.append(str(command))
			
                if cog.qualified_name in ["UserUtility"]:
                    general_commands.extend(commands)
                    commands.clear()
                elif cog.qualified_name in ["Moderation", "Guild Management"]:
                    mod_commands.extend(commands)
                    commands.clear()
                elif cog.qualified_name in ["MusicCommands"]:
                    music_commands.extend(commands)
                    commands.clear()
                else:
                    commands.clear()

            embed.set_thumbnail(url=self.bot.user.avatar_url)
            
            embed.add_field(name="General Commands", value=formatter("\n".join(general_commands)).codeblock(), inline=True)
            embed.add_field(name="Mod Commands", value=formatter("\n".join(mod_commands)).codeblock(), inline=True)
            embed.add_field(name="Music Commands", value=formatter("\n".join(music_commands)).codeblock(), inline=True)

            await ctx.send(embed=embed)
        else:
            cmd = self.bot.get_command(cmd)

            if cmd is None:
                await ctx.send("Unknown command.")
                return

            if cmd.hidden == True:
                await ctx.send("This command is hidden.")
                return

            if cmd.usage is None:
                await ctx.send(formatter(f"{cmd} - {cmd.help}").qoute())
            else:
                await ctx.send(formatter(f"{cmd} {' '.join(f'{formatter(arg).block()}' for arg in cmd.usage.split())} - {cmd.help}").qoute())

    @commands.command()
    async def info(self, ctx):
        embed = discord.Embed(
            title=self.bot.user.name,
            description="I'm powered by [discord.py](https://github.com/Rapptz/discord.py)."
        )
        embed.color = 0x2F3136
        embed.set_footer(text="desu")

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(UserUtility(bot))
