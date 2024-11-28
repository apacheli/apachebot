import discord
from discord.ext import commands


class Utility(commands.Cog):
    pass


async def setup(bot):
    await bot.add_cog(Utility(bot))
