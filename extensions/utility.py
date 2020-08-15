import discord, asyncio
from discord.ext import commands
from utils import database as db
from utils.messaging import formatter

class Utility(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def profile(self, ctx, *, member: discord.Member=None):
        await asyncio.sleep(0.8) # let the database catch up

        if member == None:
            member = ctx.author

        embed = discord.Embed(
            title=formatter(f"{member}").bold(),
            description=f"I've seen **{db.get_message_count(member)}** messages sent by **{member.name}**.\n"
            f"Level: **{int(db.get_experience(member) / 50) + 1}**\n"
            f"Experience: **{db.get_experience(member):.2f}**\n",
            color=0x36393F,
            timestamp=ctx.message.created_at
        )
        embed.set_thumbnail(url=member.avatar_url)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Utility(bot))
