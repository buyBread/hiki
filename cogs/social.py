import discord
import random
import asyncio

from discord.ext import commands
from time import time

from lib.embed import construct_embed
from lib.enums import embed_color

from utils.database import GlobalDatabase, GuildDatabase
from utils.time import seconds_to_time, format_time_long

class Social(commands.Cog, name="Social Commands"):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message) -> None:
        if message.author.bot:
            return

        author = message.author

        db        = GuildDatabase(message.guild)
        db_global = GlobalDatabase(self.bot.guilds)

        if len(message.content) > random.randint(4, 10):
            should_give_exp = True
        elif len(message.content) == 0:
            if len(message.attachments) > 0:
                should_give_exp = True
        else:
            should_give_exp = False

        if should_give_exp:           
            new_server_xp = db.get_member_data(author)["EXP"] + random.uniform(2, 4)
            db.update_member_data(author, "exp", new_server_xp)

            author_lvl = db_global.get_member_data(author)["LEVEL"]

            new_global_exp = db_global.get_member_data(author)["EXP"] + (random.uniform(2, 4) / (author_lvl / 2))
            db_global.update_member_data(author, "exp", new_global_exp)
        
            if new_global_exp > 50:
                db_global.update_member_data(author, "exp", new_global_exp - 50)
                db_global.update_member_data(author, "level", author_lvl + 1)

                await message.channel.send(
                    embed=construct_embed(
                        title="Level Up.",
                        description=f"{author.mention} you've leveled up to level {author_lvl + 1}",
                        color=embed_color["DEFAULT"]
                    )
                )

        del db
        del db_global

    @commands.command(aliases=["reputation"])
    async def rep(self, ctx, member: discord.Member = None):
        if member is None:
            return await ctx.send("Provide a Member.")
        elif member == ctx.author:
            return await ctx.send("You can't give yourself reputation.")

        db = GlobalDatabase(self.bot.guilds)

        author_data = db.get_member_data(ctx.author)
        member_data = db.get_member_data(member)

        can_give_rep = False

        if author_data["LAST_REP"] != "":
            author_last_rep = float(author_data["LAST_REP"])

            if (time() - author_last_rep) > 86400:
                can_give_rep = True
        else:
            can_give_rep = True

        if can_give_rep:
            db.update_member_data(member, "reputation", member_data["REPUTATION"] + 1)
            db.update_member_data(ctx.author, "last_rep", time())

            await ctx.send(f"> {ctx.author.mention} gave {member.mention} a reputation point.")
        else:
            cooldown = seconds_to_time(86400 - (time() - author_last_rep))

            await ctx.send(
                f"You can give reputation again in **{format_time_long(cooldown)}**."
            )

    @commands.command(aliases=["top"])
    async def leaderboard(self, ctx) -> None:
        await asyncio.sleep(1) # let the database catch up

        # index discord.Member object: all_member_data[i][0]
        # index member data: all_member_data[i][1]
        all_member_data = GuildDatabase(ctx.guild).get_all_members()
        author_data     = [ctx.author, GuildDatabase(ctx.guild).get_member_data(ctx.author)]

        all_member_data.sort(
            key=lambda x: x[1]["EXP"],
            reverse=True
        )

        embed = construct_embed(
            title=f"`{ctx.guild}`  Leaderboard",
            color=embed_color["DEFAULT"]
        )

        embed.description = f"You are rank `#{(all_member_data.index(author_data)) + 1}` on this server."
        embed.set_thumbnail(url="https://files.catbox.moe/alavwx.gif")

        server_leaderboard = ""

        for i in range(0, 10):
            member_data = all_member_data[i]
            
            server_leaderboard += f"**{i + 1}.** `{member_data[0].name}` "
            server_leaderboard += f'with {round(member_data[1]["EXP"])} Exp.'  
            server_leaderboard += "\n"

        embed.add_field(name="Top 10 Members", value=server_leaderboard)

        await ctx.send(embed=embed)

    # this is scuffed beyond repair
    # i've no idea how to do this in a different way

    @commands.command()
    async def profile(self, ctx, *args) -> None:
        if ctx.invoked_subcommand == None:
            member = None

            if len(args) == 0:
                member = ctx.author
            elif args[0] == "customize":
                return await self.profile_customize(ctx, *args)
            else:
                if len(args) == 1:
                    try:
                        member = await ctx.guild.fetch_member(args[0])
                    except discord.HTTPException:
                        name = " ".join(arg for arg in args)

                        for m in ctx.guild.members:
                            if m.nick == name or m.name == name:
                                member = m

            if member == None:
                return await ctx.send("Couldn't find the specified member.")
            elif member.bot:
                return await ctx.send("Robots don't have profiles..")

            await asyncio.sleep(1) # let the database catch up

            member_data = GlobalDatabase(self.bot.guilds).get_member_data(member)

            if member_data["EMOJI"] == "" or member_data["EMOJI"] == "none":
                title = f"{member.name}"
            else:
                title = f"{member_data['EMOJI']}   {member.name}"

            if member_data["DESCRIPTION"] == "" or member_data["DESCRIPTION"] == "none":
                description = "No description set."
            else:
                description = member_data["DESCRIPTION"]

            try:
                color = embed_color[member_data["COLOR"]]
            except KeyError:
                color = int(f"{member_data['COLOR']}", base=16)

            embed = construct_embed(title=title, description=description, color=color)

            embed.set_thumbnail(url=member.avatar_url)
            embed.set_footer(text=f"Use [{ctx.prefix}profile customize] to check out customization options.")

            embed.add_field(
                name="Level", 
                value=f'{member_data["LEVEL"]} ({(member_data["EXP"] + ((member_data["LEVEL"] - 1) * 50)):.2f} Exp.)',
            )
            embed.add_field(
                name="Reputation", 
                value=member_data["REPUTATION"],
            )
            embed.add_field(
                name="Account Created at",
                value=member.created_at.strftime("%d %B %Y, %H:%M"),
                inline=False
            )
            embed.add_field(
                name="Joined the Server at",
                value=member.joined_at.strftime("%d %B %Y, %H:%M")
            )
            embed.add_field(
                name="Server Roles",
                value=", ".join(f'<@&{role.id}>' for role in member.roles),
                inline=False
            )

            await ctx.send(embed=embed)

    async def profile_customize(self, ctx, *args) -> None:
        if len(args) > 1:
            author = ctx.author

            if args[1] == "emoji":
                try:
                    if args[2].lower() == "none":
                        GlobalDatabase(self.bot.guilds).update_member_data(author, "emoji", "'none'")
                    else:
                        GlobalDatabase(self.bot.guilds).update_member_data(author, "emoji", f"'{str(args[2])}'")
                    
                    return await ctx.send("Profile Emoji updated.")
                except IndexError:
                    return await ctx.send("Provide an Emoji. Example: :desktop:")
            elif args[1] == "color":
                try:
                    if "0x" in args[2]:
                        GlobalDatabase(self.bot.guilds).update_member_data(author, "color", f"'{str(args[2])}'")
                    else:
                        GlobalDatabase(self.bot.guilds).update_member_data(author, "color", f"'{str(args[2]).upper()}'")
                    
                    return await ctx.send("Profile embed Color updated.")
                except IndexError:
                    colors = [
                        "red", "dark_red", "cherry", "orange", "tangerine",
                        "yellow", "acid", "lime", "green", "dark_green", "cyan",
                        "light_blue", "blue", "ink", "dark_blue", "purple",
                        "dark_purple", "magenta", "pink", "light_pink"
                    ]

                    return await ctx.send(f">>> Available Colors: {'  '.join(f'`{color}`' for color in colors)}")
            elif args[1] == "description":
                try:
                    GlobalDatabase(self.bot.guilds).update_member_data(author, "description", f"'{str(args[2])}'")

                    return await ctx.send("Profile Description updated.")
                except IndexError:
                    return await ctx.send("Provide a Description.")
            else:
                return await ctx.send("Unknown action..")
        else:
            embed = construct_embed(title="Profile Customization", color=embed_color["DEFAULT"])
            
            embed.set_thumbnail(url="https://files.catbox.moe/dmtt29.gif")

            embed.add_field(
                name="emoji",
                value="Adds an emoji next to your name.\nSet to \"none\" to have no emoji.\nCustom emojis are not supported.",
                inline=False
                )       
            embed.add_field(
                name="color",
                value="Changes the Color of the embed.\nSet to \"default\" to remove embed color.\nCustom HTML Colors are supported (example: 0xff0055).",
                inline=False
            )           
            embed.add_field(
                name="description",
                value="Adds a custom description to your profile.\nSet to \"none\" to have no description on your profile.\nNOTE: wrap your description in qoutes (\"Cool description\").",
                inline=False
            )

            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Social(bot))
