import datetime
import discord
from discord.ext import commands
from discord.utils import snowflake_time
import math
import sys


class Utility(commands.Cog):
    @commands.command(aliases=["date"])
    async def time(self, ctx: commands.Context):
        """Show the time"""
        await ctx.reply(f"<t:{math.floor(datetime.datetime.now().timestamp())}>")

    @commands.command()
    async def ping(self, ctx: commands.Context):
        """pong"""
        await ctx.reply("pong")

    @commands.command(aliases=["stats"])
    async def info(self, ctx: commands.Context):
        """Get bot information"""
        uptime = datetime.datetime.now() - ctx.bot.ready_at
        embed = discord.Embed(
            title=ctx.bot.user.name,
            description=ctx.bot.application.description,
            color=int(ctx.bot.config["bot"]["color"], 16),
        )
        embed.add_field(name="Python", value=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}", inline=True)
        embed.add_field(name="Version", value="1.0.0", inline=True)
        embed.add_field(name="discord.py", value=discord.__version__, inline=True)
        embed.add_field(name="Guilds", value=len(ctx.bot.guilds), inline=True)
        embed.add_field(name="Users", value=len(ctx.bot.users), inline=True)
        embed.add_field(name="Latency", value=f"{ctx.bot.latency * 1000:.2f} ms", inline=True)
        embed.add_field(name="Uptime", value=f"{uptime.total_seconds() / 60:.2f} m", inline=True)
        embed.add_field(name="CPU Usage", value=f"{ctx.bot.process.cpu_percent():.2f}%", inline=True)
        embed.add_field(name="Memory Usage", value=f"{ctx.bot.process.memory_full_info().uss / 1024 ** 2:.2f} MiB", inline=True)
        await ctx.reply(embed=embed)

    @commands.command(aliases=["userinfo", "who", "whois", "member", "memberinfo"])
    @commands.guild_only()
    async def user(self, ctx: commands.Context, member: discord.Member):
        """Get user information"""

    @commands.command(aliases=["guildinfo", "server", "serverinfo"])
    @commands.guild_only()
    async def guild(self, ctx: commands.Context):
        """Get guild information"""

    @commands.command(aliases=["channelinfo"])
    @commands.guild_only()
    async def channel(self, ctx: commands.Context, channel: discord.abc.GuildChannel):
        """Get channel information"""

    @commands.command(aliases=["roleinfo"])
    @commands.guild_only()
    async def role(self, ctx: commands.Context, role: discord.Role):
        """Get role information"""

    @commands.command(aliases=["emojiinfo", "emote", "emoteinfo"])
    @commands.guild_only()
    async def emoji(self, ctx: commands.Context, emoji: discord.Emoji):
        """Get emoji information"""

    @commands.command()
    @commands.guild_only()
    async def message(self, ctx: commands.Context, message: discord.Message):
        """Get message information"""

    async def tag(self, ctx: commands.Context):
        pass


async def setup(bot):
    await bot.add_cog(Utility(bot))
