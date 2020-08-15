import discord

# For sending messages, embeds and files to specific channels
class channel:

    def __init__(self, guild, channel):
        self.guild = guild
        self.channel = discord.utils.get(self.guild.channels, name=channel)

    async def send(self, text: str):
        await self.channel.send(text)

    async def send_embed(self, embed: discord.Embed):
        await self.channel.send(embed=embed)

    async def send_file(self, file):
        await self.channel.send(file=discord.File(file))

# For easy message formatting
class formatter:

	def __init__(self, string):
		self.string = string

	def bold(self):
		return f"**{self.string}**"

	def italic(self):
		return f"*{self.string}*"

	def underline(self):
		return f"__{self.string}__"

	def strikethrough(self):
		return f"~~{self.string}~~"

	def block(self):
		return f"`{self.string}`"

	def codeblock(self):
		return f"```{self.string}```"

	def qoute(self):
		return f">>> {self.string}"