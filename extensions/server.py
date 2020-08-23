import discord, asyncio, os
from discord import VerificationLevel
from discord.ext import commands
from utils.messaging import formatter
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

class GuildManagement(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # todo:
    # - add invite manager

    @commands.group()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def guild(self, ctx):
        if ctx.invoked_subcommand == None:
            embed = discord.Embed(title=ctx.guild.name)
            embed.color = 0x2F3136
            embed.set_thumbnail(url=ctx.guild.icon_url)

            embed.add_field(
                name="Guild Management Commands",
                value="\n".join(f'{formatter(x).block()}' for x in ctx.command.commands),
                inline=False
            )

            await ctx.send(embed=embed)

    @guild.command(name="verification")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def change_guild_verification(self, ctx, *, level: str = None):
        if level == None:
            await ctx.send(
                "You didn't say which security level to set.\n"
                "Available levels:\n"
                "`none`\n`low`\n`medium`\n`high`\n`highest`"
            )
            return

        if level.lower() == "none":
            await ctx.guild.edit(verification_level=VerificationLevel.none)
        elif level.lower() == "low":
            await ctx.guild.edit(verification_level=VerificationLevel.low)
        elif level.lower() == "medium":
            await ctx.guild.edit(verification_level=VerificationLevel.medium)
        elif level.lower() == "high":
            await ctx.guild.edit(verification_level=VerificationLevel.high)
        elif level.lower() == "highest":
            await ctx.guild.edit(verification_level=VerificationLevel.highest)

        await ctx.send(formatter(f"Guild verification set to **{level.lower()}**.").qoute())

    @guild.group(name="invites")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def guild_invites(self, ctx):
        if ctx.invoked_subcommand == None:
            embed = discord.Embed(title="Invites")
            embed.description = f"Run `{ctx.prefix}guild invites delete [code]` to delete an invite."
            embed.color = 0x2F3136
            embed.set_thumbnail(url=ctx.guild.icon_url)

            for invite in await ctx.guild.invites():
                expiration = ""
                if invite.max_age != 0:
                    seconds = int(invite.max_age - (datetime.utcnow() - invite.created_at).total_seconds())
                    minutes = 0
                    hours = 0
                
                    while seconds > 60:
                        minutes += 1
                        if (minutes >= 60):
                            minutes = 0
                            hours += 1
                        seconds -= 60

                    expiration = f"{hours}h {minutes}min {seconds}s"
                else:
                    expiration = "Infinite"

                embed.add_field(
                    name=invite.code,
                    value=f"Creator: {invite.inviter}\n"
                    f"Expires in: {expiration}\n"
                    f"Uses: {invite.uses}\n",
                    inline=True
                )

            await ctx.send(embed=embed)

    @guild_invites.command(name="delete")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def delete_guild_invite(self, ctx, code = None):
        if code == None:
            await ctx.send("Provide an invite code.")
            return

        await (await self.bot.fetch_invite(code)).delete()
        await ctx.send(formatter(f"Invite **{code}** was deleted.").qoute())

def setup(bot):
    bot.add_cog(Moderation(bot))
    bot.add_cog(GuildManagement(bot))
