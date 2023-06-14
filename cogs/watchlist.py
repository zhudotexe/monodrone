import disnake
from disnake.ext import commands

import constants
from utils import get_user


class Watchlist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.the_list = bot.db.jget("watchlist", [])

    # ==== listeners ====
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not self.bot.is_ready():
            return
        if member.id not in self.the_list:
            return
        destination = self.bot.get_channel(constants.OUTPUT_CHANNEL_ID)
        embed = disnake.Embed(
            title="Member Joined",
            description=f"{member.mention} (`{member!s}`, `{member.id}`), who is on the list, just joined.",
            color=0x1B998B,
        )
        embed.set_thumbnail(url=str(member.display_avatar.url))
        embed.set_footer(text=f"ID: {member.id}")
        await destination.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if not self.bot.is_ready():
            return
        if member.id not in self.the_list:
            return
        destination = self.bot.get_channel(constants.OUTPUT_CHANNEL_ID)
        embed = disnake.Embed(
            title="Member Left",
            description=f"{member.mention} (`{member!s}`, `{member.id}`), who is on the list, just left.",
            color=0xF46036,
        )
        embed.set_thumbnail(url=str(member.display_avatar.url))
        embed.set_footer(text=f"ID: {member.id}")
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
        embed = disnake.Embed(
            title="Member Changed Nick",
            description=f"{before.display_name} is now known as {after.display_name} ({after.mention}).",
            color=0xC5D86D,
        )
        embed.set_thumbnail(url=str(after.display_avatar.url))
        embed.set_footer(text=f"ID: {after.id}")
        await destination.send(embed=embed)

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        if not self.bot.is_ready():
            return
        if after.id not in self.the_list:
            return
        destination = self.bot.get_channel(constants.OUTPUT_CHANNEL_ID)
        embed = disnake.Embed(
            title="Member Updated Profile",
            description=f"{before}'s username is now {after} ({after.mention}).",
            color=0xC5D86D,
        )
        embed.set_thumbnail(url=str(after.display_avatar.url))
        embed.set_footer(text=f"ID: {after.id}")
        await destination.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        if not self.bot.is_ready():
            return
        if user.id not in self.the_list:
            return

        # remove from list
        try:
            self.the_list.remove(user.id)
            self.bot.db.jset("watchlist", self.the_list)
        except ValueError:
            pass

        # send notification
        destination = self.bot.get_channel(constants.OUTPUT_CHANNEL_ID)
        embed = disnake.Embed(
            title="Member Banned",
            description=(
                f"{user.mention} (`{user!s}`, `{user.id}`), who is on the list, was just banned.\n"
                "I've removed them from the list."
            ),
            color=0xF46036
        )
        embed.set_thumbnail(url=str(user.display_avatar.url))
        embed.set_footer(text=f"ID: {user.id}")
        await destination.send(embed=embed)

    # ==== commands ====
    @commands.group(invoke_without_command=True, aliases=["list"])
    async def watchlist(self, ctx):
        if constants.MOD_ROLE_ID not in set(r.id for r in ctx.author.roles):
            return

        in_guild = []
        not_in_guild = []
        for mid in self.the_list:
            member = ctx.guild.get_member(mid)
            if member is None:
                not_in_guild.append(mid)
            else:
                in_guild.append(member)

        # build strings for each member on the list
        in_guild_strs = [f"{m.mention} (`{m!s}`, `{m.id}`)" for m in in_guild]
        not_in_guild_strs = [f"`{m}` (<@{m}>)" for m in not_in_guild]

        # break into args to create embeds with
        in_guild_chunks = [""]
        not_in_guild_chunks = [""]

        for s in in_guild_strs:
            if len(s) + len(in_guild_chunks[-1]) < 2000:
                in_guild_chunks[-1] = f"{in_guild_chunks[-1]}\n{s}".strip()
            else:
                in_guild_chunks.append(s)

        chunk_len = 1000
        for s in not_in_guild_strs:
            if len(s) + len(not_in_guild_chunks[-1]) < chunk_len:
                not_in_guild_chunks[-1] = f"{not_in_guild_chunks[-1]}\n{s}".strip()
            else:
                chunk_len = 2000
                not_in_guild_chunks.append(s)

        # build the embeds
        embeds = [disnake.Embed(title="Watchlist", description=in_guild_chunks[0])]
        for chunk in in_guild_chunks[1:]:
            embeds.append(disnake.Embed(description=chunk))
        if not_in_guild_chunks[0]:
            embeds[-1].add_field(name="Not in Server", value=not_in_guild_chunks[0])
        for chunk in not_in_guild_chunks[1:]:
            embeds.append(disnake.Embed(description=chunk))

        for embed in embeds:
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

    @watchlist.command()
    async def clean(self, ctx):
        if constants.MOD_ROLE_ID not in set(r.id for r in ctx.author.roles):
            return

        banned_users = await ctx.guild.bans().flatten()
        ban_id_map = {be.user.id: be for be in banned_users}

        # clean
        cleaned_ban_entries = []
        for uid in self.the_list.copy():
            if uid not in ban_id_map:
                continue
            self.the_list.remove(uid)
            cleaned_ban_entries.append(ban_id_map[uid])
        self.bot.db.jset("watchlist", self.the_list)

        # build output
        ban_reasons = "\n".join(
            f"`{ban_entry.user!s}` (`{ban_entry.user.id}`) - Ban reason: {ban_entry.reason}"
            for ban_entry in cleaned_ban_entries
        )
        out = f"Cleaned {len(cleaned_ban_entries)} banned users from the list.\n{ban_reasons}"

        # send (maybe long?)
        for i in range(0, len(out), 2000):
            await ctx.send(out[i : i + 2000])


def setup(bot):
    bot.add_cog(Watchlist(bot))
