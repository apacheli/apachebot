import discord
from discord.ext import commands


class Experience(commands.Cog):
    """Commands for handling experience levels."""
    help_emoji = ":test_tube:"
    help_color = 0x6dc24e

    @commands.command(aliases=["rank", "lvl"])
    async def level(self, ctx: commands.Context):
        """Show your level"""

    @commands.command(aliases=["lb"])
    async def leaderboard(self, ctx: commands.Context):
        """Show the XP leaderboard for the server"""

    @commands.command()
    async def daily(self, ctx: commands.Context):
        """List daily tasks"""

    @commands.command()
    async def shop(self, ctx: commands.Context):
        """Open the shop"""


async def setup(bot):
    await bot.add_cog(Experience(bot))
