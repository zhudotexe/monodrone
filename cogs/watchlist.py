import discord
from discord.ext import commands

import constants
from utils import get_user


class Watchlist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.the_list = bot.db.jget("watchlist", [])

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not self.bot.is_ready():
            return
        if member.id not in self.the_list:
            return
        destination = self.bot.get_channel(constants.OUTPUT_CHANNEL_ID)
        embed = discord.Embed(title="Member Joined", description=f"{member.mention}, who is on the list, just joined.",
                              color=0x1b998b)
        embed.set_thumbnail(url=str(member.avatar_url))
        await destination.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if not self.bot.is_ready():
            return
        if member.id not in self.the_list:
            return
        destination = self.bot.get_channel(constants.OUTPUT_CHANNEL_ID)
        embed = discord.Embed(title="Member Left", description=f"{member.mention}, who is on the list, just left.",
                              color=0xf46036)
        embed.set_thumbnail(url=str(member.avatar_url))
        await destination.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if not self.bot.is_ready():
            return
        if after.id not in self.the_list:
            return
        if before.nick == after.nick:
            return
        destination = self.bot.get_channel(constants.OUTPUT_CHANNEL_ID)
        embed = discord.Embed(title="Member Changed Nick",
                              description=f"{before.display_name} is now known as {after.display_name} ({after.mention}).",
                              color=0xc5d86d)
        embed.set_thumbnail(url=str(after.avatar_url))
        await destination.send(embed=embed)

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        if not self.bot.is_ready():
            return
        if after.id not in self.the_list:
            return
        destination = self.bot.get_channel(constants.OUTPUT_CHANNEL_ID)
        embed = discord.Embed(title="Member Updated Profile",
                              description=f"{before}'s username is now {after} ({after.mention}).",
                              color=0xc5d86d)
        embed.set_thumbnail(url=str(after.avatar_url))
        await destination.send(embed=embed)

    @commands.group(invoke_without_command=True, aliases=['list'])
    async def watchlist(self, ctx):
        if constants.MOD_ROLE_ID not in set(r.id for r in ctx.author.roles):
            return

        embed = discord.Embed(title="Watchlist", description="\n".join(f"<@{i}>" for i in self.the_list))
        await ctx.send(embed=embed)

    @watchlist.command()
    async def add(self, ctx, member):
        if constants.MOD_ROLE_ID not in set(r.id for r in ctx.author.roles):
            return

        try:
            user = await get_user(ctx, member)
        except:
            return await ctx.send(f"User {member} not found. Try using the ID?")
        uid = user.id

        if uid in self.the_list:
            return await ctx.send("This user is already in the watchlist.")

        self.the_list.append(uid)
        self.bot.db.jset("watchlist", self.the_list)
        await ctx.send(f"OK, added {user} to the list.")

    @watchlist.command()
    async def remove(self, ctx, member):
        if constants.MOD_ROLE_ID not in set(r.id for r in ctx.author.roles):
            return

        try:
            user = await get_user(ctx, member)
        except:
            return await ctx.send(f"User {member} not found. Try using the ID?")
        uid = user.id

        if uid not in self.the_list:
            return await ctx.send("This user is not in the watchlist.")

        self.the_list.remove(uid)
        self.bot.db.jset("watchlist", self.the_list)
        await ctx.send(f"OK, removed {user} from the list.")


def setup(bot):
    bot.add_cog(Watchlist(bot))
