import os
from discord.ext import commands

os.system("clear")

print("Starting..", end = "\n\n")

print("Available Extensions:")
for extension in os.listdir("extensions"):
    print(f" -> {extension}")

load_all_extensions = False

print("Extensions to load (Default=all):")
print("==> ", end="")
extensions_list = input()
print() # newline

if extensions_list == "all" or "":
    load_all_extensions = True
else:
    extensions_list = extensions_list.split()

bot_client = commands.Bot(command_prefix="!")

for extension in os.listdir("extensions"):
    extension = extension[:-3]
    
    if load_all_extensions:
        bot_client.load_extension(f"extensions.{extension}")
    else:
        if extension in extensions_list:
            bot_client.load_extension(f"extensions.{extension}")

# ugly
bot_client.remove_command("help")

# god bless
bot_client.run("")