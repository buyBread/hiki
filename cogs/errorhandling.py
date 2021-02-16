import discord

from discord.ext import commands

class ErrorHandling(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error) -> None:
        error = getattr(error, "original", error)

        if hasattr(ctx.command, 'on_error'):
            return

        if isinstance(error, commands.CommandNotFound):
            return

        elif isinstance(error, commands.DisabledCommand):
            return

        elif isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(f"This command is on cooldown. Retry after {error.retry_after}s.")

        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Missing `{error.param.name}` argument.")

        elif isinstance(error, commands.TooManyArguments):
            return await ctx.send("You've provided too many arguments.")

        elif isinstance(error, commands.MissingPermissions):
            if len(error.missing_perms) > 1:
                if len(error.missing_perms) > 2:
                    permissions_required = ", ".join(perm for perm in error.missing_perms)
                else:
                    permissions_required = "` and `".join(perm for perm in error.missing_perms)
                
                fmt = f"You do not posses the `{permissions_required}` permissions."
            else:
                fmt = f"You do not posses the `{error.missing_perms[0]}` permission."

            return await ctx.send(fmt)

        elif isinstance(error, commands.CheckFailure):
            return await ctx.send("You are not allowed to use this command.")

        elif isinstance(error, commands.BadArgument):
            return await ctx.send(f"A provided argument was invalid..\n```{error}```")

        elif isinstance(error, commands.PrivateMessageOnly):
            return await ctx.send("This command only works in DMs.")

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send("This command doesn't work in DMs.")
            except discord.Forbidden:
                return

        else:
            return await ctx.send(f"> Something went wrong..\n```\n{error}```")

def setup(bot):
    bot.add_cog(ErrorHandling(bot))