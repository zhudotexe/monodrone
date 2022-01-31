import os

import discord
from discord.ext import commands
from discord.ext.commands import Bot

from jsondb import JSONDB

TOKEN = os.getenv("TOKEN")
COGS = ('cogs.watchlist', 'cogs.points', 'cogs.autodelete', 'cogs.autopublish', 'cogs.utility')


class Monodrone(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = JSONDB()


intents = discord.Intents.all()

bot = Monodrone('.', intents=intents)


# === listeners ===
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    await ctx.send(f"Error: {str(error)}")


# === commands ===
@bot.command()
async def ping(ctx):
    await ctx.send("Pong.")


for cog in COGS:
    bot.load_extension(cog)

if __name__ == '__main__':
    bot.run(TOKEN)
