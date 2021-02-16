import discord

# from lib
from lib.enums import activity_type
from lib.config import Config

def construct_activity(**kwargs) -> discord.Activity:
    return discord.Activity(**kwargs)

def construct_base_activity() -> discord.Activity:
    config = Config()

    return construct_activity(
        type=activity_type[config.return_value("activity_type").upper()],
        name=config.return_value("activity_name")
    )
