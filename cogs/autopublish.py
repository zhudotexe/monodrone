import asyncio

import discord
from discord.ext import commands

import constants

class AutoPublish(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.autopublish_channels = bot.db.jget("autopublish", {})

    @commands.Cog.listener()
    async def on_message(self, message):
        if not self.bot.is_ready():
            return
        if not message.channel.id in self.autopublish_channels:
            return
        await asyncio.sleep(0.5)  
        await message.publish()
        
    # ==== commands ====
    @commands.group(invoke_without_command=True)
    @commands.has_role(constants.MOD_ROLE_ID)
    async def autopublish(self, ctx):
        """Shows all channels with active autopublish."""
        embed = discord.Embed(colour=0x60AFFF, title="Active Autopublish Channels")
        embed.description = '\n'.join(f"<#{channel}>"
                                      for channel in self.autopublish_channels) \
                            or "No active channels."
        embed.set_footer(text="Use \".autopublish add #channel #\" to add a channel rule, "
                              "or \".autopublish remove #channel\" to remove one.")
        await ctx.send(embed=embed)

    @autopublish.command(name='add')
    @commands.has_role(constants.MOD_ROLE_ID)
    async def autopublish_add(self, ctx, channel: discord.TextChannel):
        """Adds or updates an autopublish rule for the given channel."""
        self.autopublish_channels[channel.id] = True
        self.bot.db.jset("autopublish", self.autopublish_channels)
        await ctx.send(f"Okay, added autopublish rule to publish messages in {channel.mention}.")

    @autopublish.command(name='remove')
    @commands.has_role(constants.MOD_ROLE_ID)
    async def autopublish_remove(self, ctx, channel: discord.TextChannel):
        """Removes an autopublish rule from a channel."""
        if channel.id not in self.autopublish_channels:
            return await ctx.send(f"{channel.mention} has no autopublish rule.")
        del self.autopublish_channels[channel.id]
        self.bot.db.jset("autopublish", self.autopublish_channels)
        await ctx.send(f"Okay, removed autopublish rule from {channel.mention}.")


def setup(bot):
    bot.add_cog(AutoPublish(bot))
