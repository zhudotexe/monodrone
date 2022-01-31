import discord
from discord.ext import commands
from discord.utils import DISCORD_EPOCH

import constants


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role(constants.MOD_ROLE_ID)
    async def snowtime(self, ctx, *ids):
        """Shows the timestamp each given snowflake was created at."""
        if not ids:
            await ctx.send("Please pass in at least 1 ID.")
            return

        out = []
        for snowflake in ids:
            try:
                snowflake = int(snowflake)
            except ValueError:
                out.append(f"`{snowflake}` is not a valid ID.")
                continue

            snowflake_timestamp = int(((snowflake >> 22) + DISCORD_EPOCH) / 1000)
            out.append(f"`{snowflake}` -> <t:{snowflake_timestamp}:f> (<t:{snowflake_timestamp}:R>)")
        await ctx.send('\n'.join(out))


def setup(bot):
    bot.add_cog(Utility(bot))
