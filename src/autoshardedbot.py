import json
import sys
from time import time

from src.utils.constructors import construct_activity

import discord
from discord.ext.commands import AutoShardedBot

class Hiki(AutoShardedBot):
    def __init__(self) -> None:
        # gatekeep
        if sys.platform == "win32":
            exit("Use WSL.")

        # obvs init the original
        super().__init__(
            intents=discord.Intents.all(),
            command_prefix="pl4c3h0ld3r") # super prefix
        
        try:
            with open("config.json", "r") as fp:
                self.config = json.load(fp)
        except FileNotFoundError:
            sys.exit("Config file not found.")

        # replaced with infinitely better thing
        # cogs.utility.help_command
        self.remove_command("help")

    async def get_channel_latency(self, channel: discord.TextChannel) -> float:
        old = time()

        async with channel.typing():
            return time() - old

    async def on_ready(self):
        # can't do per guild? not sure why
        await self.tree.sync() 
        
        await self.change_presence(
            activity=construct_activity(
                type=self.config["activity_type"],
                name=self.config["activity_name"]
            ))
