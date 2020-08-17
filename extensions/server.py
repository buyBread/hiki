import asyncio, os
from discord.ext import commands
from datetime import datetime

class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(usage="limit")
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, limit: int):
        """Delete a specified amount of messages."""       
        logs = f"#{ctx.channel}\n\n"
        log_file_name = f"clear_log_{datetime.utcnow()}.txt" # so we don't desync
        async for message in ctx.channel.history(limit=limit+1):
            logs += f"{message.created_at} | {message.author} ({message.author.id}): {message.content}\n"
            with open(os.path.join("clear_logs", log_file_name), "w") as f:
                f.write(logs)

        # fix this later
        await ctx.channel.purge(limit=limit+1)

        self.bot.dispatch("clear_invoked", limit, ctx.channel, ctx.author, log_file_name)       

def setup(bot):
    bot.add_cog(Moderation(bot))
    