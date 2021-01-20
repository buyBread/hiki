import discord, os, asyncio
from discord import AuditLogAction
from discord.ext import commands
from random import randint
from datetime import datetime
from utils.database import DatabaseTool
from utils.cosmetic import change_presence
from utils.messaging import formatter, channel

class GeneralEvents(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Ready!", end = "\n\n")
        await change_presence(self.bot, "watching", "for >help")

        for guild in self.bot.guilds:
            DatabaseTool(guild).check_guild()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return

        DatabaseTool(member.guild).add_guild_member(member)

    @commands.Cog.listener()
    async def on_message(self, message):
        author = message.author

        if author.bot:
            return

        db = DatabaseTool(message.guild)

        message_count = db.get_member_data(author)[0]
        db.update_member_data(author, "messages", message_count + 1)

        del db

class ErrorHandling(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        error = getattr(error, 'original', error)

        if isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(formatter(f"{formatter(error.param.name).block()} is missing\n").qoute())
        else:
            await ctx.send(formatter(f"Something went wrong.. {formatter(error).codeblock()}").qoute())

# relays audit log information + custom events
class AuditLog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # todo:
    # - log guild changes

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return

        embed = discord.Embed(title="A member has joined the server.", timestamp=datetime.utcnow())
        embed.description = f"Username: {member}\nUser ID: {member.id}\nAccount Date: {member.created_at.strftime('%Y/%m/%d')}"
        embed.set_thumbnail(url=member.avatar_url)
        embed.color=0x2F3136

        await channel(member.guild, "audit").send_embed(embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.bot:
            return

        embed = discord.Embed(title="A member has left the server.", timestamp=datetime.utcnow())
        embed.description = f"Username: {member}\nUser ID: {member.id}"
        embed.set_thumbnail(url=member.avatar_url)
        embed.color = 0x2F3136

        async for entry in member.guild.audit_logs(limit=1):
            if entry.action == AuditLogAction.ban:
                if entry.target == member:
                    embed.color = 0xFF3030
                    embed.add_field(name="Reason", value=f"Banned by {entry.user.mention}", inline=False)
            elif entry.action == AuditLogAction.kick:
                if entry.target == member:
                    embed.color = 0xFCDB03
                    embed.add_field(name="Reason", value=f"Kicked by {entry.user.mention}", inline=False)

        await channel(member.guild, "audit").send_embed(embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.author.bot:
            return
        if len(before.content) == 0:
            return
        if len(after.embeds) != 0:
            return

        embed = discord.Embed(title="Message edited.", timestamp=datetime.utcnow())
        embed.description = f"Username: {after.author}\nUser ID: {after.author.id}"
        embed.set_thumbnail(url=after.author.avatar_url)
        embed.color = 0xACF00E
        
        embed.add_field(name="Before", value=before.content, inline=False)
        embed.add_field(name="After", value=after.content, inline=False)
        
        await channel(after.guild, "audit").send_embed(embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        if len(message.embeds) != 0:
            return

        embed = discord.Embed(title="Message deleted.", timestamp=datetime.utcnow())
        embed.description = f"Username: {message.author}\nUser ID: {message.author.id}"
        embed.set_thumbnail(url=message.author.avatar_url)
        embed.color = 0xEE28FC

        embed.add_field(name="Content", value=message.content, inline=False)

        # get the responsible moderator and check if a bot deleted the message(s)
        async for entry in message.guild.audit_logs(limit=1):
            if entry.action == AuditLogAction.message_delete:
                if entry.user.bot:
                    return

                if entry.target == message.author:

                    embed.title = f"A message by {message.author} has been deleted."
                    embed.add_field(name="Responsible", value=entry.user, inline=False)

        await channel(message.guild, "audit").send_embed(embed)

    @commands.Cog.listener()
    async def on_clear_invoked(self, limit, chan, member, log_file):
        embed = discord.Embed(title=f"{limit} messages cleared in `#{chan}`.", timestamp=datetime.utcnow())
        embed.description = f"Username: {member}\nUser ID: {member.id}"
        embed.set_thumbnail(url=member.avatar_url)
        embed.color= 0xFF5EBC

        await channel(chan.guild, "audit").send_embed(embed)
        await channel(chan.guild, "audit").send_file(f"clear_logs/{log_file}")

        await asyncio.sleep(1)

        os.remove(f"clear_logs/{log_file}")

def setup(bot):
    bot.add_cog(GeneralEvents(bot))
    bot.add_cog(ErrorHandling(bot))
    bot.add_cog(AuditLog(bot))
