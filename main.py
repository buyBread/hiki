import sys

from lib.autoshardedbot import AutoShardedBot

if __name__ == "__main__":
    if sys.platform == "win32":
        exit("Use WSL.")

    bot = AutoShardedBot()
