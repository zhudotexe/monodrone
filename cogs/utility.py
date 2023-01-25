import asyncio

import disnake
from disnake.ext import commands
from disnake.utils import DISCORD_EPOCH

import constants


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.message_command(name="Alert Mods")
    async def mod_ping(self, inter: disnake.MessageCommandInteraction):
        """Allows a user to send an alert to moderators, linking to a specific message."""

        mod_ping_channel = await inter.guild.fetch_channel(constants.MOD_PING_CHANNEL)
        now = datetime.datetime.now()
        timestamp = int(now.timestamp())

        message = inter.target

        embed = disnake.Embed(title=f"{inter.author.name} has requested a moderator", timestamp=now)
        embed.set_author(name=inter.author.name, icon_url=inter.author.avatar.url)
        embed.description = f"Requested by {inter.author.mention} in {inter.channel.mention}\n" \
                            f"<t:{timestamp}> (<t:{timestamp}:R>)\n\n" \
                            f"[The request was for this message]({message.jump_url}) by {message.author.mention}"
        embed.add_field(name="Message Contents", value=message.content[:2000])

        await mod_ping_channel.send(embed=embed)

        await inter.send(
            f"Moderators have been pinged for [this Message]({message.jump_url}).",
            ephemeral=True,
            suppress_embeds=True
        )

    @commands.message_command(name="Private Thread")
    async def message_private_thread(self, inter: disnake.MessageCommandInteraction):
        """For moderators/staff to quickly create a private thread for a particular user, via that users message."""
        await self._private_thread(inter, inter.target.author)

    @commands.user_command(name="Private Thread")
    async def user_private_thread(self, inter: disnake.UserCommandInteraction):
        """For moderators/staff to quickly create a private thread for a particular user, via that user."""
        await self._private_thread(inter, inter.target)

    async def _private_thread(self, inter: disnake.ApplicationCommandInteraction, target: disnake.Member):
        """Creates a private thread in the given channel (or #moderator-support if in #moderator-alerts) and invites the user."""

        if inter.channel_id == 1067223029861580831:  # moderator-alerts
            channel = inter.guild.get_channel(568911894459711490)  # moderator-support
        else:
            channel = inter.channel

        thread: disnake.Thread = await channel.create_thread(
            name=f"{target.name} Private Thread",
            type=disnake.ChannelType.private_thread,
            invitable=False,
        )

        await thread.send(
            f"Hello {target.mention}, this is a private thread, visible only to you and the moderator team."
        )
        await thread.add_user(inter.author)

        await inter.send(f"The private thread {thread.mention} has been created.", ephemeral=True)

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
        await ctx.send("\n".join(out))


def setup(bot):
    bot.add_cog(Utility(bot))
