import datetime
import io

import discord
from discord.ext import commands, tasks

import constants


# data schema:
# autodelete.json: dict int->int channel->days

class AutoDelete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.autodelete_channels = bot.db.jget("autodelete", {})
        self.deleter.start()

    def cog_unload(self):
        self.deleter.cancel()

    # ==== tasks ====
    @tasks.loop(hours=1)
    async def deleter(self):
        await self.bot.wait_until_ready()
        log_channel = self.bot.get_channel(constants.OUTPUT_CHANNEL_ID)
        for channel_id, days in self.autodelete_channels.items():
            # get channel
            channel = self.bot.get_channel(int(channel_id))
            if channel is None:
                continue
            print(f"Starting autodelete on #{channel.name}...")

            # delete and log
            try:
                delete_log = io.StringIO()
                deleted = await channel.purge(limit=None,
                                              before=datetime.datetime.utcnow() - datetime.timedelta(days=days))
                for message in deleted:
                    delete_log.write(f"[{message.created_at.isoformat()}] {message.author} ({message.author.id})\n"
                                     f"{message.content}\n\n")
                if not deleted:
                    continue
                delete_log.seek(0)
                await log_channel.send(f"Deleted {len(deleted)} messages from {channel.mention}.",
                                       file=discord.File(delete_log, filename=f"{channel.name}-deleted.log"))
            except discord.HTTPException as e:
                print(e)
                await log_channel.send(f"Unable to delete messages from {channel.mention}: {e}")

    # ==== commands ====
    @commands.group(invoke_without_command=True)
    @commands.has_role(constants.MOD_ROLE_ID)
    async def autodelete(self, ctx):
        """Shows all channels with active autodelete."""
        embed = discord.Embed(colour=0x60AFFF, title="Active Autodelete Channels")
        embed.description = '\n'.join(f"<#{channel}>: {days} days"
                                      for channel, days in self.autodelete_channels.items()) \
                            or "No active channels."
        embed.set_footer(text="Use \".autodelete add #channel #\" to add a channel rule, "
                              "or \".autodelete remove #channel\" to remove one.")
        await ctx.send(embed=embed)

    @autodelete.command(name='add')
    @commands.has_role(constants.MOD_ROLE_ID)
    async def autodelete_add(self, ctx, channel: discord.TextChannel, days: int):
        """Adds or updates an autodelete rule for the given channel."""
        if days < 1:
            return await ctx.send("Days must be at least 1.")
        self.autodelete_channels[channel.id] = days
        self.bot.db.jset("autodelete", self.autodelete_channels)
        await ctx.send(f"Okay, added autodelete rule to delete messages older than {days} days from {channel.mention}.")

    @autodelete.command(name='remove')
    @commands.has_role(constants.MOD_ROLE_ID)
    async def autodelete_remove(self, ctx, channel: discord.TextChannel):
        """Removes an autodelete rule from a channel."""
        if channel.id not in self.autodelete_channels:
            return await ctx.send(f"{channel.mention} has no autodelete rule.")
        del self.autodelete_channels[channel.id]
        self.bot.db.jset("autodelete", self.autodelete_channels)
        await ctx.send(f"Okay, removed autodelete rule from {channel.mention}.")


def setup(bot):
    bot.add_cog(AutoDelete(bot))
