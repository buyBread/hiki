import discord, asyncio
from discord.ext import commands
from utils import database as db
from utils.messaging import formatter
from datetime import datetime

class UserUtility(commands.Cog, name="User Utility"):
    
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
        if member == None:
            member = ctx.author

        if member.bot:
            await ctx.send("Bot's don't have profiles.. :(")
            return

        await asyncio.sleep(0.6) # let the database catch up

        embed = discord.Embed(
            title=f"Profile of {member}",
            description=
            f"I've seen **{db.get_message_count(member)}** messages sent by **{member.name}**.\n"
            f"Level: **{db.get_level(member)}**\n"
            f"Experience: **{(((db.get_level(member) - 1) * 50) + db.get_experience(member)):.2f}**",
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

        description = ""
        top_users = db.get_top_users(self.bot.get_all_members())
        for i in range(0, 10):
            user_data = top_users[i]
            description += f"{i+1}. **{user_data[0]}** (Level: {db.get_level(user_data[0])}) - **{user_data[1]:.2f}** Experience\n"

        embed.description = description

        await ctx.send(embed=embed)

class HelpfulCommands(commands.Cog, name="Help"):

    def __init__(self, bot):
        self.bot = bot

    # todo: make this not suck and introduce more help commands

    @commands.command(usage="command")
    async def help(self, ctx, cmd = None):
        """Displays and shows usage of available commands."""
        if cmd == None:       
            embed = discord.Embed(
                title="Help Page",
                description=
                "This is a list of available commands.\n"
                f"Use `{ctx.prefix}help [command]` to see it's usage.", 
                timestamp=datetime.utcnow()
            )
            embed.color = 0x2F3136

            commands = []

            for cog in self.bot.cogs: # this doesn't give an actual cog
                cog = self.bot.get_cog(cog) # so get it here

                for command in cog.walk_commands():
                    if command.hidden == True:
                        pass
                    elif command in commands:
                        pass
                    elif command.parent != None:
                        pass
                    else:
                        commands.append(command)
			
                if commands != []:
                    embed.add_field(
                        name=cog.qualified_name,
                        value=" ".join([formatter(command).block() for command in commands]),
                        inline=True
                    )

                commands.clear() # clear the commands list once we're ready to iterate the next cog
		
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
    bot.add_cog(HelpfulCommands(bot))
