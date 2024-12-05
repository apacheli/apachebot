import discord
from discord.ext import commands


class Developer(commands.Cog):
    pass


async def setup(bot):
    await bot.add_cog(Developer(bot))
