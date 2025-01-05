import aiohttp
import datetime
import discord
from discord.ext import commands
from discord.utils import snowflake_time
import math
import sys


class Utility(commands.Cog):
    emoji = ":gear:"
    description = "Utility commands."
    color = 0x808080

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
    async def user(self, ctx: commands.Context, member: discord.Member = None):
        """Get user information"""
        if member == None:
            member = ctx.author
        description = ""
        for activity in member.activities:
            if activity.type == discord.ActivityType.playing:
                description += f"- Playing **{activity.name}**\n"
            elif activity.type == discord.ActivityType.streaming:
                description += f"- Streaming [**{activity.name}**]({activity.url})\n"
            elif activity.type == discord.ActivityType.listening:
                description += f"- Listening to [**{activity.title}**]({activity.track_url})\n"
            elif activity.type == discord.ActivityType.watching:
                description += f"- Watching **{activity.name}**\n"
            elif activity.type == discord.ActivityType.custom:
                emoji = f"{activity.emoji} " if activity.emoji else ""
                description += f"- {emoji}{activity.name}\n"
            elif activity.type == discord.ActivityType.competing:
                description += f"- Competing in **{activity.name}**\n"
        _statuses = {
            discord.Status.online: "Online",
            discord.Status.idle: "Idle",
            discord.Status.dnd: "Do Not Disturb",
            discord.Status.offline: "Offline",
        }
        alt_name = member.nick or member.global_name
        tag_name = f"{member.name}{f"#{member.discriminator}" if member.discriminator != "0" else ""}"
        embed = discord.Embed(
            title=f"{alt_name or tag_name}{f" ({tag_name})" if alt_name else ""}",
            description=description,
            color=member.color,
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Status", value=_statuses[member.status], inline=True)
        embed.add_field(name="Joined", value=f"<t:{math.floor(member.joined_at.timestamp())}>", inline=True)
        embed.add_field(name="Created", value=f"<t:{math.floor(member.created_at.timestamp())}>", inline=True)
        if len(member.roles) > 1:
            sorted_roles = sorted(member.roles[1:], key=lambda r: r.position, reverse=True)
            embed.add_field(
                name="Roles",
                value=" ".join([role.mention for role in sorted_roles]),
            )
        embed.set_footer(text=member.id)
        await ctx.send(embed=embed)

    @commands.command(aliases=["guildinfo", "server", "serverinfo"])
    @commands.guild_only()
    async def guild(self, ctx: commands.Context):
        """Get guild information"""
        embed = discord.Embed(
            title=ctx.guild.name,
            description=ctx.guild.description,
        )
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)
        embed.add_field(name="Created", value=f"<t:{math.floor(ctx.guild.created_at.timestamp())}>", inline=True)
        embed.add_field(name="Channels", value=len(ctx.guild.channels), inline=True)
        embed.add_field(name="Emojis", value=len(ctx.guild.emojis), inline=True)
        embed.add_field(name="Members", value=len(ctx.guild.members), inline=True)
        embed.add_field(name="Roles", value=len(ctx.guild.roles), inline=True)
        embed.set_footer(text=ctx.guild.id)
        await ctx.send(embed=embed)

    @commands.command(aliases=["channelinfo"])
    @commands.guild_only()
    async def channel(self, ctx: commands.Context, channel: discord.abc.GuildChannel):
        """Get channel information"""

    @commands.command(aliases=["roleinfo"])
    @commands.guild_only()
    async def role(self, ctx: commands.Context, role: discord.Role):
        """Get role information"""

    @commands.command(name="emoji", aliases=["emojiinfo", "emote", "emoteinfo"])
    @commands.guild_only()
    async def _emoji(self, ctx: commands.Context, emoji: discord.Emoji):
        """Get emoji information"""

    @commands.command()
    @commands.guild_only()
    async def message(self, ctx: commands.Context, message: discord.Message):
        """Get message information"""

    @commands.command()
    async def tag(self, ctx: commands.Context):
        pass


async def setup(bot):
    await bot.add_cog(Utility(bot))
