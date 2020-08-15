import discord, asyncio
from discord.ext import commands
from utils import database as db
from utils.messaging import formatter

class UserUtility(commands.Cog, name="User Utility"):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(usage="member")
    async def profile(self, ctx, *, member: discord.Member=None):
        """Display a Member's profile."""
        await asyncio.sleep(0.6) # let the database catch up

        if member == None:
            member = ctx.author

        embed = discord.Embed(
            title=formatter(f"{member}").bold(),
            description=
            f"I've seen **{db.get_message_count(member)}** messages sent by **{member.name}**.\n"
            f"Level: **{db.get_level(member)}**\n"
            f"Experience: **{(((db.get_level(member) - 1) * 50) + db.get_experience(member)):.2f}**",
            color=0x36393F,
            timestamp=ctx.message.created_at
        )
        embed.set_thumbnail(url=member.avatar_url)

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
                "Enter a command to see it's usage.",
                color=0x36393F,
                timestamp=ctx.message.created_at
            )
            embed.set_thumbnail(url=self.bot.user.avatar_url)

            commands = []

            for cog in self.bot.cogs: # this doesn't give an actual cog
                cog = self.bot.get_cog(cog) # so get it here

                for command in cog.walk_commands():
                    if command.hidden == True:
                        pass
                    elif command in commands:
                        pass
                    else:
                        commands.append(command)
			
                if commands != []:
                    embed.add_field(
                        name=formatter(cog.qualified_name).bold(),
                        value="\n ".join([f"{command} - {command.help}" for command in commands]),
                        inline=False
                    )

                commands.clear() # clear the commands list once we're ready to iterate the next cog
		
            await ctx.send(embed=embed)
        else:
            cmd = self.bot.get_command(cmd)
            await ctx.send(formatter(f"{cmd} {'  '.join(f'{formatter(x).block()}' for x in cmd.usage.split())} - {cmd.help}").qoute())

def setup(bot):
    bot.add_cog(UserUtility(bot))
    bot.add_cog(HelpfulCommands(bot))
