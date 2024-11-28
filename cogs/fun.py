import asyncio
import discord
from discord.ext import commands


class Entertainment(commands.Cog):
    pass


async def setup(bot):
    await bot.add_cog(Entertainment(bot))
