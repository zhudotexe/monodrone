import asyncio

from discord.ext.commands import BadArgument, MemberConverter


async def get_user(ctx, member):
    try:
        return await MemberConverter().convert(ctx, member)
    except BadArgument:
        return await ctx.bot.fetch_user(int(member))


def auth_and_chan(ctx):
    """Message check: same author and channel"""

    def chk(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    return chk


def get_positivity(string):
    if isinstance(string, bool):  # oi!
        return string
    lowered = string.lower()
    if lowered in ('yes', 'y', 'true', 't', '1', 'enable', 'on'):
        return True
    elif lowered in ('no', 'n', 'false', 'f', '0', 'disable', 'off'):
        return False
    else:
        return None


async def confirm(ctx, message, delete_msgs=False):
    """
    Confirms whether a user wants to take an action.
    :rtype: bool|None
    :param ctx: The current Context.
    :param message: The message for the user to confirm.
    :param delete_msgs: Whether to delete the messages.
    :return: Whether the user confirmed or not. None if no reply was recieved
    """
    msg = await ctx.channel.send(message)
    try:
        reply = await ctx.bot.wait_for('message', timeout=30, check=auth_and_chan(ctx))
    except asyncio.TimeoutError:
        return None
    replyBool = get_positivity(reply.content) if reply is not None else None
    if delete_msgs:
        try:
            await msg.delete()
            await reply.delete()
        except:
            pass
    return replyBool
