import discord
from discord.ext import commands


class Entertainment(commands.Cog):
    emoji = "\N{VIDEO GAME}"
    description = "Entertainment commands."
    color = 0x5cc433


async def setup(bot):
    await bot.add_cog(Entertainment(bot))
