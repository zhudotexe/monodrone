import asyncio

import disnake
from disnake.ext import commands
from disnake.utils import DISCORD_EPOCH

import constants


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.message_command(name="Private Thread")
    async def message_private_thread(self, inter: disnake.MessageCommandInteraction):
        """For moderators/staff to quickly create a private thread for a particular user, via that users message."""
        await self._private_thread(inter, inter.target.author)

    @commands.user_command(name="Private Thread")
    async def user_private_thread(self, inter: disnake.UserCommandInteraction):
        """For moderators/staff to quickly create a private thread for a particular user, via that user."""
        await self._private_thread(inter, inter.target)

    async def _private_thread(self, inter: disnake.ApplicationCommandInteraction, target: disnake.Member):
        thread: disnake.Thread = await inter.channel.create_thread(name=f"{target.name} Private Thread",
                                                                   type=disnake.ChannelType.private_thread,
                                                                   invitable=False)

        await thread.send(
            f"Hello {target.mention}, this is a private thread, visible only to you and the moderator team."
        )
        await thread.add_user(inter.author)

        await inter.send(f"Thread {thread.mention} created.", ephemeral=True)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: disnake.abc.GuildChannel, after: disnake.abc.GuildChannel):
        """Updates the permissions in the #appeal channel to allow the muted role to send messages in threads"""

        # We only care about the #appeal channel
        if before.id != 854369754236190780:
            return

        muted_role = before.guild.get_role(554336698381762592)

        # I found not giving it a little time would not save it properly
        await asyncio.sleep(2)
        await after.set_permissions(muted_role, send_messages_in_threads=True)

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
