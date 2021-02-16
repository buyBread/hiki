import discord
import os

from discord.ext import commands
from datetime import datetime

from lib.message import MessageData

class Moderator(commands.Cog, name="Mod Commands"):

	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@commands.has_permissions(manage_messages=True)
	async def kick(self, ctx, member: discord.Member, reason: str = None) -> None:
		member.kick(reason=reason)
		await ctx.send(f"> {member} has been kicked.")

	@commands.command()
	@commands.has_permissions(manage_messages=True)
	async def ban(self, ctx, member: discord.Member, reason: str = None) -> None:
		member.ban(reason=reason)
		await ctx.send(f"> {member} has been banned.")

	@commands.command(aliases=["clear"])
	async def prune(self, ctx, limit: int) -> None:
		if limit < 1:
			return await ctx.send("Invalid value.")

		channel  = ctx.channel
		messages = []

		async for message in channel.history(limit=limit+1):
			messages.append(
				MessageData(message.content, message.channel, message.author, message.created_at)
			)

		await channel.purge(limit=limit + 1)

		self.bot.dispatch("channel_prune", channel, messages, ctx.author)

	async def cog_check(self, ctx):
		if isinstance(ctx.channel, discord.DMChannel):
			await ctx.send("You cannot use Moderation commands in DMs")
			return False

		return True

def setup(bot):
	bot.add_cog(Moderator(bot))