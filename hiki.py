import asyncio
import os

from src.autoshardedbot import Hiki

# Evertyhing is preconfigured in the class.
bot = Hiki()

async def load_cogs() -> None:
    for cog in os.listdir("src/cogs"):
        # remove ".py"
        await bot.load_extension(f"src.cogs.{cog[:-3]}")

if __name__ == "__main__":
    # extension loading is a coroutine now (2.0)
    asyncio.run(load_cogs())

    bot.run(bot.config["discord_token"])
