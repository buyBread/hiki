from discord import Activity, ActivityType

async def change_presence(bot, type: str, text: str):
    if type.lower() == "playing":
        await bot.change_presence(activity=Activity(type=ActivityType.playing, name=text))
    elif type.lower() == "streaming":
        await bot.change_presence(activity=Activity(type=ActivityType.streaming, name=text))
    elif type.lower() == "watching":
        await bot.change_presence(activity=Activity(type=ActivityType.watching, name=text))
    elif type.lower() == "listening":
        await bot.change_presence(activity=Activity(type=ActivityType.listening, name=text))
