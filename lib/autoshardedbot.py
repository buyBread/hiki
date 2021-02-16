import discord
import os
import sys

from discord.ext import commands
from time import time
from typing import Union

from lib.presence import construct_base_activity
from lib.config import Config

from utils.database import GlobalDatabase, GuildDatabase

class AutoShardedBot(commands.AutoShardedBot):

    def __init__(self):
        print("Initializing..")

        self.config = Config()

        self.startup_time = time()

        super().__init__(
            command_prefix=self.config.return_value("base_prefix"),
            intents=discord.Intents.all()
        )

        # default command is ugly
        self.remove_command("help")

        for cog in os.listdir("cogs"):
            self.load_extension(f"cogs.{cog[:-3]}")
            print(f"Loaded: {cog}")

        self.run(self.get_token())

    def get_token(self) -> str:
        token = os.getenv("BOT_TOKEN")

        if token == None:
            sys.exit("BOT_TOKEN not found.")

        return token           

    async def get_latency(self, channel) -> float:
        """
        * @channel: discord.TextChannel object
        """
        otime = time()
        async with channel.typing():    
            return time() - otime

    async def get_user(self, ctx, user) -> Union[discord.Member, discord.User, None]:
        """
        * @ctx: the command Context
        * @user: the User's name or ID
        """

        if user is None:
            return ctx.author

        for member in ctx.guild.members:
            if member.name == user or str(member.id) in str(user):
                return member

        try:
            return await self.fetch_user(int(user))
        except (discord.NotFound, TypeError, ValueError) as e:
            return None

    def get_channel_by_name(self, guild, channel_name) -> discord.TextChannel:
        """
        * @guild: discord.Guild object
        * @channel_name
        """
        return discord.utils.get(guild.channels, name=channel_name)

    async def on_ready(self) -> None:
        print("Connected")

        await self.change_presence(activity=construct_base_activity())

        GlobalDatabase(self.guilds).initialize()

        for guild in self.guilds:
            GuildDatabase(guild).initialize()

    async def on_guild_join(self, guild) -> None:
        GuildDatabase(guild).initialize()

    async def on_member_join(self, member) -> None:
        if GuildDatabase(member.guild).check_member(member) == False:
            GuildDatabase(member.guild).add_guild_member(member)

        if GlobalDatabase(self).check_member(member) == False:
            GlobalDatabase(self).add_guild_member(member)
