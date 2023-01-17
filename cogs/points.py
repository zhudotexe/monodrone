import asyncio
import datetime

import disnake
from disnake.ext import commands

import constants
from utils import confirm, get_user


class Infraction:
    def __init__(self, points: int, reason: str, timestamp: datetime.datetime, mod_id: int):
        self.points = points
        self.reason = reason
        self.timestamp = timestamp
        self.mod_id = mod_id

    @classmethod
    def new(cls, points, reason, mod_id):
        return cls(points, reason, datetime.datetime.now(), mod_id)

    @classmethod
    def from_dict(cls, d):
        return cls(d['points'], d['reason'], datetime.datetime.fromtimestamp(d['timestamp']), d['mod_id'])

    def to_dict(self):
        return {'points': self.points, 'reason': self.reason, 'timestamp': self.timestamp.timestamp(),
                'mod_id': self.mod_id}


def get_infractions_for(bot, user):
    return [Infraction.from_dict(i) for i in bot.db.jget(f"{user.id}-points", [])]


def tag_active(infs):
    """Given a list of infractions, returns a list of tuples (Infraction, active)."""
    sorted_infs = sorted(infs, key=lambda inf: inf.timestamp)
    last_unexpired = datetime.datetime.now()

    out = []
    for inf in reversed(sorted_infs):  # latest first
        if inf.timestamp + datetime.timedelta(seconds=constants.POINTS_EXPIRY_TIME) > last_unexpired:
            out.insert(0, (inf, True))
            last_unexpired = inf.timestamp
        else:
            out.insert(0, (inf, False))

    return out


def recommended_action_for(points, user):
    recommendation = ("{long} mute. Dyno command: `?mute {user} {short} You have received a {long} mute for <reason>. "
                      "If you wish to discuss or appeal this mute, please follow the instructions in #appeal`")
    if points < 10:  # 0-10
        return "No action."
    elif points < 20:  # 10-20
        return recommendation.format(long="1 hour", short="1h", user=user.id)
    elif points < 30:  # 20-30
        return recommendation.format(long="24 hour", short="24h", user=user.id)
    elif points < 40:  # 30-40
        return recommendation.format(long="3 day", short="3d", user=user.id)
    elif points < 50:  # 40-50
        return recommendation.format(long="7 day", short="7d", user=user.id)
    else:  # 50+
        return f"Permanent ban. Dyno command: `?ban {user.id} You have been banned from the D&D Beyond discord server for <reason>`"


def get_points(infractions):
    """Gets the total number of active points, their expiry, and lifetime points from a tagged list of infractions."""
    if not infractions:
        return 0, datetime.datetime.now(), 0
    active = sum(inf.points for inf, active in infractions if active)
    expiry = infractions[-1][0].timestamp + datetime.timedelta(seconds=constants.POINTS_EXPIRY_TIME)
    lifetime_points = sum(inf.points for inf, _ in infractions)
    return active, expiry, lifetime_points


# data scheme:
# <ID>-points.json = list of Infraction

class Points(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if not self.bot.is_ready():
            return
        if message.guild is None:
            return
        if message.author.bot:
            return
        if constants.MOD_ROLE_ID not in set(r.id for r in message.author.roles):
            return
        if not message.content.startswith('?warn '):
            return
        await asyncio.sleep(0.5)  # ensure Dyno can respond first
        await message.channel.send(
            f"Was that a warning? Make sure to log the points with `.points add @user # REASON`!\n"
            f"(for example, `.points add @zhu.exe#4211 5 spamming and stuff`)")

    @commands.group(invoke_without_command=True)
    async def points(self, ctx, member):
        """Lists the active points for a user."""
        if constants.MOD_ROLE_ID not in set(r.id for r in ctx.author.roles):
            return

        try:
            user = await get_user(ctx, member)
        except:
            return await ctx.send(f"User {member} not found. Try using the ID?")

        user_infractions = get_infractions_for(self.bot, user)

        descriptions = []
        active_points = 0
        if not user_infractions:
            descriptions.append("This user has no points. Hooray!")
        else:
            infractions = tag_active(user_infractions)

            for (i, (infraction, active)) in enumerate(infractions):
                inf_desc = f"`[{i}]` {infraction.points} points - {infraction.reason} " \
                           f"(<@{infraction.mod_id}>, {infraction.timestamp})"
                if not active:
                    inf_desc = f"~~{inf_desc}~~"
                descriptions.append(inf_desc)

            active_points, expiry, lifetime_points = get_points(infractions)
            if active_points:
                descriptions.append(f"\n{user} has {active_points} active points expiring at {expiry}, "
                                    f"and {lifetime_points} lifetime points.")
            else:
                descriptions.append(f"\n{user} has no active points, and {lifetime_points} lifetime points.")

        embeds = [disnake.Embed(title=f"Points for {user}", color=0xF8333C, description='')]
        for line in descriptions:
            if len(embeds[-1].description) + len(line) >= 2048:
                embeds.append(disnake.Embed(color=0xF8333C, description=''))
            embeds[-1].description = f"{embeds[-1].description}\n{line}"

        if active_points:
            embeds[-1].add_field(name="Recommended Action", value=recommended_action_for(active_points, user),
                                 inline=False)
        for embed in embeds:
            await ctx.send(embed=embed)

    @points.command(name='add')
    async def points_add(self, ctx, member, num: int, *, reason):
        if constants.MOD_ROLE_ID not in set(r.id for r in ctx.author.roles):
            return

        try:
            user = await get_user(ctx, member)
        except:
            return await ctx.send(f"User {member} not found. Try using the ID?")

        user_infractions = get_infractions_for(self.bot, user)
        new_infraction = Infraction.new(num, reason, ctx.author.id)
        user_infractions.append(new_infraction)

        self.bot.db.jset(f"{user.id}-points", [i.to_dict() for i in user_infractions])

        infractions = tag_active(user_infractions)

        embed = disnake.Embed(title=f"Points Added for {user}", color=0xFCAB10)
        embed.description = f"Added {new_infraction.points} points to {user} for {new_infraction.reason}."
        active_points, expiry, lifetime_points = get_points(infractions)

        embed.add_field(name="Points", inline=False,
                        value=f"{user} has {active_points} active points expiring at {expiry}, "
                              f"and {lifetime_points} lifetime points.")
        embed.add_field(name="Recommended Action", value=recommended_action_for(active_points, user), inline=False)

        await ctx.send(embed=embed)

    @points.command(name='remove')
    async def points_remove(self, ctx, member, index: int):
        if constants.MOD_ROLE_ID not in set(r.id for r in ctx.author.roles):
            return

        try:
            user = await get_user(ctx, member)
        except:
            return await ctx.send(f"User {member} not found. Try using the ID?")

        user_infractions = get_infractions_for(self.bot, user)
        infractions = tag_active(user_infractions)
        if index < 0 or index >= len(infractions):
            return await ctx.send("Invalid index. Use `.points @user` to view infraction indices.")
        removed, active = infractions[index]
        del infractions[index]

        confirmed = await confirm(
            ctx,
            f"Are you sure you want to remove the {removed.points} point infraction for {removed.reason} "
            f"from {user}? (yes/no)")

        if not confirmed:
            return await ctx.send("Confirmation aborted or timed out.")

        self.bot.db.jset(f"{user.id}-points", [i.to_dict() for i, _ in infractions])

        embed = disnake.Embed(title=f"Infraction Removed for {user}", color=0x6BBF59)
        embed.description = f"Removed {removed.points} points from {user} for {removed.reason}."
        active_points, expiry, lifetime_points = get_points(infractions)

        embed.add_field(name="Points", inline=False,
                        value=f"{user} has {active_points} active points expiring at {expiry}, "
                              f"and {lifetime_points} lifetime points.")
        embed.add_field(name="Recommended Action", value=recommended_action_for(active_points, user), inline=False)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Points(bot))
