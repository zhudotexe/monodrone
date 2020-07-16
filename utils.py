from discord.ext.commands import BadArgument, MemberConverter


async def get_user(ctx, member):
    try:
        return await MemberConverter().convert(ctx, member)
    except BadArgument:
        return await ctx.bot.fetch_user(int(member))
