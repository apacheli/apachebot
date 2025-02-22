import discord
from discord.ext import commands


class Developer(commands.Cog):
    """Commands for development purposes."""
    help_emoji = "\N{DESKTOP COMPUTER}"
    help_color = 0x4885cf


async def setup(bot):
    await bot.add_cog(Developer(bot))
