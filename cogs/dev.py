import asyncio
import datetime
import discord
from discord.ext import commands


class Developer(commands.Cog):
    @commands.command()
    async def info(self, ctx):
        return

    @commands.command()
    async def ping(self, ctx: commands.Context):
        await ctx.reply("pong")


async def setup(bot):
    await bot.add_cog(Developer(bot))
