import discord

activity_type = {
    "PLAYING": discord.ActivityType.playing,
    "WATCHING": discord.ActivityType.watching,
    "STREAMING": discord.ActivityType.streaming,
    "LISTENING": discord.ActivityType.listening,
    "COMPETING": discord.ActivityType.competing,
    "CUSTOM": discord.ActivityType.custom,
    "UNKNOWN": discord.ActivityType.unknown,
}

status_type = {
    "ONLINE": discord.Status.online,
    "OFFLINE": discord.Status.offline,
    "IDLE": discord.Status.idle,
    "DND": discord.Status.dnd,
    "INVISIBLE": discord.Status.invisible,
}
