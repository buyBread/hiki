import discord, os
from discord import AuditLogAction
from discord.ext import commands
from random import randint
from datetime import datetime
from utils import database as db
from utils.cosmetic import change_presence
from utils.messaging import formatter, channel

class GeneralEvents(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Ready!", end = "\n\n")
        await change_presence(self.bot, "listening", "Subwoofer Lullaby")

        db.setup_users(self.bot.get_all_members())

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return

        db.add_user(member)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        author = message.author

        db.update_message_count(author)

        # to somewhat mitigate spam
        should_update_level = False
        if len(message.content) > randint(4, 12):
            should_update_level = True
        elif len(message.content) == 0:
            if len(message.attachments) > 0:
                should_update_level = True

        if should_update_level:
            # store to a variable before updating the database
            old_level = db.get_level(author)
            db.update_level(author)
            new_level = db.get_level(author)

            if (old_level < new_level):
                await message.channel.send(formatter(f"{author.mention} **{new_level}**").qoute())

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

        embed = discord.Embed(title=f"{member} has joined the server.", timestamp=datetime.utcnow())
        embed.description = f"User ID: {member.id}\nAccount Date: {member.created_at.strftime('%Y/%m/%d')}"
        embed.color=0x2F3136

        await channel(member.guild, "audit").send_embed(embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.bot:
            return

        embed = discord.Embed(title=f"{member} has left the server.", timestamp=datetime.utcnow())
        embed.description = f"User ID: {member.id}"
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

        embed = discord.Embed(title=f"{after.author} has edited a message.", timestamp=datetime.utcnow())
        embed.description = f"User ID: {after.author.id}"
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

        embed = discord.Embed(title=f"{message.author} has deleted a message.", timestamp=datetime.utcnow())
        embed.description = f"User ID: {message.author.id}"
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
    async def on_clear_invoked(self, limit, chan, user, log_file):
        embed = discord.Embed(title=f"{user} cleared {limit} messages in `#{chan}`.", timestamp=datetime.utcnow())
        embed.description = f"User ID: {user.id}"
        embed.color= 0xFF5EBC

        await channel(chan.guild, "audit").send_embed(embed)
        await channel(chan.guild, "audit").send_file(f"clear_logs/{log_file}")

def setup(bot):
    bot.add_cog(GeneralEvents(bot))
    bot.add_cog(ErrorHandling(bot))
    bot.add_cog(AuditLog(bot))
