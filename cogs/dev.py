import discord
from discord.ext import commands


class Developer(commands.Cog):
    emoji = "\N{DESKTOP COMPUTER}"
    description = "Developer commands."
    color = 0x808000


async def setup(bot):
    await bot.add_cog(Developer(bot))
