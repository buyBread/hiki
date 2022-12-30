# Aesthetic reasons

import discord

from src.utils.enums import activity_type

def construct_activity(**kwargs) -> discord.Activity:
    kwargs["type"] = activity_type[kwargs["type"].upper()]

    return discord.Activity(**kwargs)

def construct_embed(**kwargs) -> discord.Embed:
    return discord.Embed(**kwargs)
