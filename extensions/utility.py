from utils import database as db
from datetime import datetime
import discord
from discord.ext import commands

class Utility(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def messages(self, ctx, *, member: discord.Member=None):
        if member == None:
            member = ctx.author

        embed = discord.Embed(
            title="Message Count",
            description=f"I've seen **{member}** send {db.get_message_count(member)} messages.",
            color=member.top_role.color,
            timestamp=datetime.now()
            )
        embed.set_thumbnail(url=member.avatar_url)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Utility(bot))