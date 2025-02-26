import discord
from discord.ext import commands


class Experience(commands.Cog):
    """Commands for handling experience levels."""
    help_emoji = ":test_tube:"
    help_color = 0x6dc24e

    @commands.command(aliases=["rank", "lvl"])
    async def level():
        """Show your level"""
        pass

    @commands.command(aliases=["lb"])
    async def leaderboard():
        """Show the XP leaderboard for the server"""
        pass

    @commands.command()
    async def daily():
        """List daily tasks"""
        pass


async def setup(bot):
    await bot.add_cog(Experience(bot))
