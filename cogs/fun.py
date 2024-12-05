import discord
from discord.ext import commands


class Entertainment(commands.Cog):
    @commands.command()
    async def roll(self, ctx):
        pass


async def setup(bot):
    await bot.add_cog(Entertainment(bot))
