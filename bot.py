import os

import discord
from discord.ext import commands
from discord.ext.commands import BadArgument, Bot, MemberConverter

import constants
from jsondb import JSONDB

TOKEN = os.getenv("TOKEN")

bot = Bot('.')
db = JSONDB()
the_list = db.jget("watchlist", [])


# === listeners ===
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    await ctx.send(f"Error: {str(error)}")


@bot.event
async def on_member_join(member):
    if not bot.is_ready():
        return
    if member.id not in the_list:
        return
    destination = bot.get_channel(constants.OUTPUT_CHANNEL_ID)
    embed = discord.Embed(title="Member Joined", description=f"{member.mention}, who is on the list, just joined.",
                          color=0x1b998b)
    embed.set_thumbnail(url=str(member.avatar_url))
    await destination.send(embed=embed)


@bot.event
async def on_member_remove(member):
    if not bot.is_ready():
        return
    if member.id not in the_list:
        return
    destination = bot.get_channel(constants.OUTPUT_CHANNEL_ID)
    embed = discord.Embed(title="Member Left", description=f"{member.mention}, who is on the list, just left.",
                          color=0xf46036)
    embed.set_thumbnail(url=str(member.avatar_url))
    await destination.send(embed=embed)


@bot.event
async def on_member_update(before, after):
    if not bot.is_ready():
        return
    if after.id not in the_list:
        return
    if before.nick == after.nick:
        return
    destination = bot.get_channel(constants.OUTPUT_CHANNEL_ID)
    embed = discord.Embed(title="Member Changed Nick",
                          description=f"{before.display_name} is now known as {after.display_name} ({after.mention}).",
                          color=0xc5d86d)
    embed.set_thumbnail(url=str(after.avatar_url))
    await destination.send(embed=embed)


@bot.event
async def on_user_update(before, after):
    if not bot.is_ready():
        return
    if after.id not in the_list:
        return
    destination = bot.get_channel(constants.OUTPUT_CHANNEL_ID)
    embed = discord.Embed(title="Member Updated Profile",
                          description=f"{before}'s username is now {after} ({after.mention}).",
                          color=0xc5d86d)
    embed.set_thumbnail(url=str(after.avatar_url))
    await destination.send(embed=embed)


# === commands ===
@bot.command()
async def ping(ctx):
    await ctx.send("Pong.")


@bot.group(invoke_without_command=True, aliases=['list'])
async def watchlist(ctx):
    if constants.MOD_ROLE_ID not in set(r.id for r in ctx.author.roles):
        return

    embed = discord.Embed(title="Watchlist", description="\n".join(f"<@{i}>" for i in the_list))
    await ctx.send(embed=embed)


async def get_user(ctx, member):
    try:
        return await MemberConverter().convert(ctx, member)
    except BadArgument:
        return await bot.fetch_user(int(member))


@watchlist.command()
async def add(ctx, member):
    if constants.MOD_ROLE_ID not in set(r.id for r in ctx.author.roles):
        return

    try:
        user = await get_user(ctx, member)
    except:
        return await ctx.send(f"User {member} not found. Try using the ID?")
    uid = user.id

    if uid in the_list:
        return await ctx.send("This user is already in the watchlist.")

    the_list.append(uid)
    db.jset("watchlist", the_list)
    await ctx.send(f"OK, added {user} to the list.")


@watchlist.command()
async def remove(ctx, member):
    if constants.MOD_ROLE_ID not in set(r.id for r in ctx.author.roles):
        return

    try:
        user = await get_user(ctx, member)
    except:
        return await ctx.send(f"User {member} not found. Try using the ID?")
    uid = user.id

    if uid not in the_list:
        return await ctx.send("This user is not in the watchlist.")

    the_list.remove(uid)
    db.jset("watchlist", the_list)
    await ctx.send(f"OK, removed {user} from the list.")


if __name__ == '__main__':
    bot.run(TOKEN)
