import discord
import os

from datetime import datetime
from discord import AuditLogAction
from discord.ext import commands

from lib.embed import construct_embed

from utils.database import GuildDatabase

class AuditLog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return

        embed = construct_embed(
            title="A member has joined the server.",
            description = f"Username: {member}\nUser ID: {member.id}\nAccount Date: {member.created_at.strftime('%Y/%m/%d')}\n",
            color=0x2F3136,
            timestamp=datetime.utcnow()
        )

        embed.set_thumbnail(url=member.avatar_url)

        if GuildDatabase(member.guild).check_member(member) == True:
            embed.description += "Member has already joined this server previously."

        channel = self.bot.get_channel_by_name(member.guild, "audit")

        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.bot:
            return

        embed = construct_embed(
            title="A member has left the server.",
            description = f"Username: {member}\nUser ID: {member.id}",
            color = 0x2F3136,
            timestamp=datetime.utcnow()
        )

        embed.set_thumbnail(url=member.avatar_url)

        async for entry in member.guild.audit_logs(limit=1):
            if entry.action == AuditLogAction.ban:
                if entry.target == member:
                    embed.color = 0xFF3030
                    embed.add_field(name="Reason", value=f"Banned by {entry.user.mention}", inline=False)
            elif entry.action == AuditLogAction.kick:
                if entry.target == member:
                    embed.color = 0xFCDB03
                    embed.add_field(name="Reason", value=f"Kicked by {entry.user.mention}", inline=False)

        channel = self.bot.get_channel_by_name(member.guild, "audit")

        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.author.bot:
            return
        if len(before.content) == 0:
            return
        if len(after.embeds) != 0:
            return

        embed = construct_embed(
            title="Message edited.",
            description = f"Username: {after.author}\nUser ID: {after.author.id}",
            color = 0xACF00E,
            timestamp=datetime.utcnow()
        )

        embed.set_thumbnail(url=after.author.avatar_url)
        
        embed.add_field(name="Before", value=before.content)
        embed.add_field(name="After", value=after.content)
        
        channel = self.bot.get_channel_by_name(after.guild, "audit")

        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        if len(message.embeds) != 0:
            return # embeds are tricky, rather just ignore them

        embed = construct_embed(
            title="Message deleted.",
            description = f"Username: {message.author}\nUser ID: {message.author.id}",
            color = 0xEE28FC,
            timestamp=datetime.utcnow()
        )

        embed.set_thumbnail(url=message.author.avatar_url)

        embed.add_field(name="Content", value=message.content, inline=False)

        async for entry in message.guild.audit_logs(limit=1):
            if entry.action == AuditLogAction.message_delete:
                if entry.user.bot:
                    return # we don't want to log bots deleting messages

                if entry.target == message.author:
                    embed.title = f"A message by {message.author} has been deleted."
                    embed.add_field(name="Responsible", value=entry.user, inline=False)

        channel = self.bot.get_channel_by_name(message.guild, "audit")

        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_channel_prune(self, chan, messages, member):
        embed = construct_embed(
            title=f"`{len(messages) - 1}` messages pruned in `#{chan}`.",
            description = f"Username: {member}\nUser ID: {member.id}",
            color= 0xFF5EBC,
            timestamp=datetime.utcnow()
        )

        embed.set_thumbnail(url=member.avatar_url)

        log_file_name = f"{chan.name}_{chan.id}_{datetime.utcnow().strftime('%Y_%m_%d_%H_%M_%S')}"

        with open(os.path.join("prune_logs", log_file_name), "w") as f:
            for message in messages:
                f.write(f"{message.created_at.strftime('%Y/%m/%d %H:%M:%S')} | {message.author} ({message.author.id}): {message.content}\n")

        channel = self.bot.get_channel_by_name(chan.guild, "audit")

        await channel.send(embed=embed)
        await channel.send(file=discord.File(f"prune_logs/{log_file_name}"))

def setup(bot):
    bot.add_cog(AuditLog(bot))
    