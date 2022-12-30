import discord

from discord.ext import commands
from discord import app_commands

from ..autoshardedbot import Hiki
from ..utils.constructors import construct_embed
from ..utils.image import get_prominent_color

class utility_cog(commands.Cog, name="Utility"):
    def __init__(self, bot: Hiki) -> None:
        super().__init__()

        self.bot = bot

    @app_commands.command(
        name="ping",
        description="Display the latency.")
    async def latency(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message( # >.>
            f"{int(round(await self.bot.get_channel_latency(interaction.channel), 3) * 1000)}ms")

    # todo: simple perms check
    @app_commands.command(
        name="help",
        description="Shows all available commands.")
    async def help_command(self, interaction: discord.Interaction) -> None:
        embed = construct_embed(
            title="Available Commands",
            description="Commands are shown based on permissions.\nIf you don't see a certain command, it is becaus you don't have the necessary permissions.",
            color=0x2F3136
        )

        embed.set_thumbnail(url=self.bot.user.avatar.url)

        for _, cog in self.bot.cogs.items():
            embed.add_field(
                name=cog.qualified_name,
                value="\n".join(
                        "**{}** ~ {}".format(cmd.qualified_name, cmd.description)
                            for cmd in cog.get_app_commands())
            )
    
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="user",
        description="Shows information about a Discord User.")
    @app_commands.describe(user="The user whose information you want to view.")
    async def user_info(self, interaction: discord.Interaction, user: discord.User = None) -> None:
        user = user or interaction.user

        embed = construct_embed(
            title=f"{user.display_name}",
            description=f"**ID**: {user.id}\n**Full**: {user.name}#{user.discriminator}\n",
            color=await get_prominent_color(user.display_avatar.with_size(64).with_format("jpg"))
        )

        embed.set_thumbnail(url=user.avatar.url)

        if interaction.guild:
            # check if user is part of this guild
            if (interaction.guild.get_member(user.id)) != None:
                embed.add_field(
                    name="Join Date",
                    value=discord.utils.format_dt(user.joined_at),
                    inline=True,
                )

        embed.add_field(
            name="Account Created",
            value=discord.utils.format_dt(user.created_at),
            inline=True,
        )
    
        await interaction.response.send_message(embed=embed)

async def setup(bot: Hiki) -> None:
    await bot.add_cog(utility_cog(bot))
