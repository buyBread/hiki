import discord

from discord import VerificationLevel
from discord.ext import commands
from datetime import datetime

from lib.embed import construct_embed

from utils.time import seconds_to_time, format_time_short

class ServerDatabase(commands.Cog, name="Server Database"):

    def __init__(self, bot):
        self.bot = bot

    # todo..

    async def cog_check(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("You cannot use Server Database commands in DMs")
            return False

        return True   

class ServerManagement(commands.Cog, name="Server Management"):

    def __init__(self, bot):
        self.bot = bot

    # add guild icon change
    # add guild name change

    @commands.group()
    async def guild(self, ctx):
        if ctx.invoked_subcommand == None:
            embed = construct_embed(
                title=ctx.guild.name,
                description=f"""ID: {ctx.guild.id}
                Member Count: {len(ctx.guild.members)}
                Owner: {ctx.guild.owner.mention}""",
                color = 0x2F3136
            )
            embed.set_thumbnail(url=ctx.guild.icon_url)

            embed.add_field(
                name="Server Management Commands",
                value="\n".join(f'**{x}**' for x in ctx.command.commands),
                inline=False
            )

            await ctx.send(embed=embed)

    @guild.command(name="verification")
    @commands.has_permissions(manage_guild=True)
    async def change_guild_verification(self, ctx, *, level: str = None):
        if level == None:
            await ctx.send(
                "You didn't say which security level to set.\n"
                "Available levels:\n"
                "`none`\n`low`\n`medium`\n`high`\n`very_high`"
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
        elif level.lower() == "very_high":
            await ctx.guild.edit(verification_level=VerificationLevel.very_high)

        await ctx.send(f"> Guild verification set to **{level.lower()}**.")

    @guild.group(name="invites")
    @commands.has_permissions(manage_guild=True)
    async def guild_invites(self, ctx):
        if ctx.invoked_subcommand == None:
            embed = construct_embed(
                title="Invites",
                description = f"Run `{ctx.prefix}guild invites delete [code]` to delete an invite.",
                color = 0x2F3136
            )
            embed.set_thumbnail(url=ctx.guild.icon_url)

            if len(await ctx.guild.invites()) == 0:
                embed.description += "\n\n**Guild has no invites.**"
            else:
                for invite in await ctx.guild.invites():
                    expiration = ""
                    # there's probably a way cleaner way to do it?
                    if invite.max_age != 0:
                        invite_time_left = (datetime.utcnow() - invite.created_at).total_seconds()
                        invite_time = seconds_to_time(invite.max_age - invite_time_left)
                        
                        expiration = format_time_short(invite_time)
                    else:
                        expiration = "Infinite"

                    embed.add_field(
                        name=invite.code,
                        value=f"""Creator: {invite.inviter}
                        Expires in: {expiration}
                        Uses: {invite.uses}""",
                        inline=True
                    )

            await ctx.send(embed=embed)

    @guild_invites.command(name="delete")
    @commands.has_permissions(manage_guild=True)
    async def delete_guild_invite(self, ctx, code = None):
        if code == None:
            await ctx.send("Provide an invite code.")
            return

        await (await self.bot.fetch_invite(code)).delete()
        await ctx.send(f"> Invite **{code}** was deleted.")

    async def cog_check(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("You cannot use Server Management commands in DMs")
            return False

        return True   

def setup(bot):
    bot.add_cog(ServerDatabase(bot))
    bot.add_cog(ServerManagement(bot))
