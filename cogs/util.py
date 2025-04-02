import datetime
import colorsys
from math import floor
import random
import sys

import discord
from discord import ActivityType, ChannelType, Status
from discord.ext import commands

from apacheutil import format_username


channel_types = {
    ChannelType.text: "Text Channels",
    ChannelType.voice: "Voice Channels",
    ChannelType.category: "Categories",
    ChannelType.news: "Announcement Channels",
    ChannelType.stage_voice: "Stages",
    ChannelType.forum: "Forums",
}

statuses = {
    Status.online: "Online",
    Status.idle: "Idle",
    Status.dnd: "Do Not Disturb",
    Status.offline: "Offline",
}

colors = {
    "Black": (0, 0, 0),
    "White": (1, 1, 1),
    "Red": (1, 0, 0),
    "Yellow": (1, 1, 0),
    "Green": (0, 1, 0),
    "Cyan": (0, 1, 1),
    "Blue": (0, 0, 1),
    "Magenta": (1, 0, 1),
    "Orange": (1, 0.5, 0),
    "Chartreuse": (0.5, 1, 0),
    "Spring Green": (0, 1, 0.5),
    "Azure": (0, 0.5, 1),
    "Violet": (0.5, 0, 1),
    "Rose": (1, 0, 0.5),
}


def closest_color(r, g, b):
    c = None
    s = float("inf")
    for color, (cr, cg, cb) in colors.items():
        distance = (r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2
        if distance < s:
            s = distance
            c = color
    return c


def rgb_to_cmyk(r, g, b):
    k = max(r, g, b)
    if k == 0:
        return (0, 0, 0, 1)
    c = 1 - r / k
    m = 1 - g / k
    y = 1 - b / k
    return (c, m, y, 1 - k)


def format_activity_text(activity: discord.Activity):
    if activity.type == ActivityType.playing:
        return f"Playing **{activity.name}**"
    if activity.type == ActivityType.streaming:
        return f"Streaming [**{activity.name}**]({activity.url})"
    if activity.type == ActivityType.listening:
        return f"Listening to [**{activity.title}**]({activity.track_url})"
    if activity.type == ActivityType.watching:
        return f"Watching **{activity.name}**"
    if activity.type == ActivityType.custom:
        emoji = f"{activity.emoji} " if activity.emoji else ""
        return f"{emoji}{activity.name}"
    if activity.type == ActivityType.competing:
        return f"Competing in **{activity.name}**"


class Utility(commands.Cog):
    """Helpful commands for whatever purpose."""
    help_emoji = ":gear:" # \N{GEAR} doesn't work for some reason
    help_color = 0x8f9496

    @commands.command()
    async def upper(self, ctx: commands.Context, *, text: str):
        """Convert text to uppercase"""
        await ctx.reply(text.upper())

    @commands.command()
    async def lower(self, ctx: commands.Context, *, text: str):
        """Convert text to lowercase"""
        await ctx.reply(text.lower())

    @commands.command()
    async def reverse(self, ctx: commands.Context, *, text: str):
        """Reverse text"""
        await ctx.reply(text[::-1])

    @commands.command()
    async def escape(self, ctx: commands.Command, message: discord.Message):
        """Escape markdown text from a message"""
        await ctx.reply(discord.utils.escape_markdown(message.content))

    @commands.command(aliases=["date"])
    async def time(self, ctx: commands.Context):
        """Show the time"""
        await ctx.reply(f"<t:{floor(datetime.datetime.now().timestamp())}>")

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
        embed.add_field(name="Python", value=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        embed.add_field(name="Version", value="2.3.1")
        embed.add_field(name="discord.py", value=discord.__version__)
        embed.add_field(name="Guilds", value=len(ctx.bot.guilds))
        embed.add_field(name="Users", value=len(ctx.bot.users))
        embed.add_field(name="Latency", value=f"{ctx.bot.latency * 1000:.2f} ms")
        embed.add_field(name="Uptime", value=f"{uptime.total_seconds() / 60:.2f} m")
        embed.add_field(name="CPU Usage", value=f"{ctx.bot.process.cpu_percent():.2f}%")
        embed.add_field(name="Memory Usage", value=f"{ctx.bot.process.memory_full_info().uss / 1024 ** 2:.2f} MiB")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["userinfo", "who", "whois", "member", "memberinfo"])
    @commands.guild_only()
    async def user(self, ctx: commands.Context, member: discord.Member = None):
        """Get user information"""
        if member is None:
            member = ctx.author
        description = ""
        for activity in member.activities:
            description += f"- {format_activity_text(activity)}\n"
        embed = discord.Embed(
            title=format_username(member),
            description=description,
            color=member.color,
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Status", value=statuses[member.status])
        embed.add_field(name="Joined", value=f"<t:{floor(member.joined_at.timestamp())}>")
        embed.add_field(name="Created", value=f"<t:{floor(member.created_at.timestamp())}>")
        if len(member.roles) > 1:
            sorted_roles = sorted(member.roles[1:], key=lambda r: r.position, reverse=True)
            embed.add_field(
                name="Roles",
                value=" ".join(role.mention for role in sorted_roles),
            )
        embed.set_footer(text=member.id)
        await ctx.reply(embed=embed)

    @commands.command(aliases=["guildinfo", "server", "serverinfo"])
    @commands.guild_only()
    async def guild(self, ctx: commands.Context):
        """Get guild information"""
        embed = discord.Embed(
            title=ctx.guild.name,
            description=ctx.guild.description,
            color=ctx.guild.owner.color,
        )
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)
        embed.add_field(name="Created", value=f"<t:{floor(ctx.guild.created_at.timestamp())}>")
        embed.add_field(name="Channels", value=len(ctx.guild.channels))
        embed.add_field(name="Members", value=len(ctx.guild.members))
        embed.add_field(name="Emojis", value=len(ctx.guild.emojis))
        embed.add_field(name="Stickers", value=len(ctx.guild.stickers))
        embed.add_field(name="Roles", value=len(ctx.guild.roles))
        embed.set_footer(text=ctx.guild.id)
        await ctx.reply(embed=embed)

    @commands.command(aliases=["channelinfo", "channels"])
    @commands.guild_only()
    async def channel(self, ctx: commands.Context, channel: discord.abc.GuildChannel = None):
        """Get channel information"""
        embed = discord.Embed(color=ctx.guild.owner.color)
        if channel is None:
            embed.set_author(
                name=ctx.guild.name,
                icon_url=ctx.guild.icon if ctx.guild.icon.url else None,
            )
            channels_map = {c: [] for c in channel_types}
            for c in ctx.guild.channels:
                channels_map[c.type].append(c)
            for channel_type in channels_map:
                channels = channels_map[channel_type]
                if len(channels) > 0:
                    embed.add_field(
                        name=channel_types[channel_type],
                        value=" ".join(f"`{c.name}`" for c in channels),
                        inline=False,
                    )
                embed.set_footer(text=f"{len(ctx.guild.channels)} channels")
            return await ctx.reply(embed=embed)
        embed.set_author(
            name=channel.name,
            icon_url=ctx.guild.icon if ctx.guild.icon.url else None,
        )
        embed.description = getattr(channel, "topic", None)
        embed.add_field(name="Type", value=channel.type)
        embed.add_field(name="Created", value=f"<t:{floor(channel.created_at.timestamp())}>")
        embed.add_field(name="NSFW", value=channel.nsfw)
        embed.set_footer(text=channel.id)
        await ctx.reply(embed=embed)

    @commands.command(aliases=["roleinfo", "roles"])
    @commands.guild_only()
    async def role(self, ctx: commands.Context, role: discord.Role = None):
        """Get role information"""
        embed = discord.Embed()
        if role is None:
            embed.color = ctx.guild.owner.color
            embed.set_author(
                name=ctx.guild.name,
                icon_url=ctx.guild.icon if ctx.guild.icon.url else None,
            )
            embed.description = " ".join(f"`{r.name}`" for r in ctx.guild.roles)
            embed.set_footer(text=f"{len(ctx.guild.roles)} roles")
            return await ctx.reply(embed=embed)
        embed.set_author(
            name=role.name,
            icon_url=ctx.guild.icon if ctx.guild.icon.url else None,
        )
        embed.color = role.color
        embed.add_field(name="Color", value=f"#{role.color.value:06x}".upper())
        embed.add_field(name="Created", value=f"<t:{floor(role.created_at.timestamp())}>")
        embed.add_field(name="Members", value=len(role.members))
        embed.add_field(name="Hoist", value=role.hoist)
        embed.add_field(name="Integration", value=role.managed)
        embed.add_field(name="Mentionable", value=role.mentionable)
        embed.set_footer(text=role.id)
        if role.display_icon is not None:
            embed.set_thumbnail(url=role.display_icon.url)
        await ctx.reply(embed=embed)

    @commands.command(name="emoji", aliases=["emojiinfo", "emote", "emoteinfo", "emojis", "emotes"])
    @commands.guild_only()
    async def _emoji(self, ctx: commands.Context, emoji: discord.Emoji = None):
        """Get emoji information"""
        embed = discord.Embed(color=ctx.guild.owner.color)
        if emoji is None:
            embed.set_author(
                name=ctx.guild.name,
                icon_url=ctx.guild.icon if ctx.guild.icon.url else None,
            )
            embed.description = " ".join(f"{e}" for e in ctx.guild.emojis)
            embed.set_footer(text=f"{len(ctx.guild.emojis)} emojis")
            return await ctx.reply(embed=embed)
        embed.set_author(name=emoji.name)
        embed.set_thumbnail(url=emoji.url)
        embed.add_field(name="Created", value=f"<t:{floor(emoji.created_at.timestamp())}>")
        embed.add_field(name="Integration", value=emoji.managed)
        embed.add_field(name="Available", value=emoji.available)
        embed.set_footer(text=emoji.id)
        await ctx.reply(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def boosters(self, ctx: commands.Context):
        """List all server boosters"""
        if not ctx.guild.premium_subscriber_role:
            return await ctx.reply(":x: No booster role.")
        embed = discord.Embed(color=ctx.guild.premium_subscriber_role.color, description="")
        count = 0
        for member in ctx.guild.premium_subscribers:
            count += 1
            embed.description += f"{count}. {format_username(member)} <t:{floor(member.premium_since.timestamp())}:R>\n"
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        embed.set_footer(text=f"{count} boosters")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["listening", "music", "song", "track"])
    @commands.guild_only()
    async def spotify(self, ctx: commands.Context, member: discord.Member = None):
        """See what someone is listening to on Spotify"""
        if member is None:
            member = ctx.author
        embeds = []
        for activity in member.activities:
            if activity.type != ActivityType.listening:
                continue
            embed = discord.Embed(
                title=activity.title,
                color=activity.color,
                url=activity.track_url,
            )
            embed.set_thumbnail(url=activity.album_cover_url)
            embed.add_field(name="Album", value=activity.album, inline=False)
            embed.add_field(name="Artists", value="\n".join(activity.artists), inline=False)
            embed.set_footer(text=format_username(member), icon_url=member.display_avatar.url)
            embeds.append(embed)
        if len(embeds) > 0:
            await ctx.reply(embeds=embeds)
        else:
            await ctx.reply(":x: No track detected.")

    @commands.command(aliases=["pfp"])
    @commands.guild_only()
    async def avatar(self, ctx: commands.Context, member: discord.Member = None):
        """Get a user's avatar"""
        await ctx.reply(member.display_avatar.url if member else ctx.author.display_avatar.url)

    @commands.command()
    @commands.guild_only()
    async def icon(self, ctx: commands.Context):
        """Get the guild's icon"""
        await ctx.reply(ctx.guild.icon.url if ctx.guild.icon else ":x: No icon found.")

    @commands.command(name="color")
    async def _color(self, ctx: commands.Context, color = None):
        """Return color information"""
        if color is None:
            color = random.randint(0, 0xffffff)
        elif (color := int(color, 16)) > 0xffffff:
            return await ctx.reply(":x: Invalid hexadecimal value.")
        r = ((color >> 16) & 0xff) / 255
        g = ((color >> 8) & 0xff) / 255
        b = (color & 0xff) / 255
        hls = colorsys.rgb_to_hls(r, g, b)
        hsv = colorsys.rgb_to_hsv(r, g, b)
        # yiq = colorsys.rgb_to_yiq(r, g, b)
        cmyk = rgb_to_cmyk(r, g, b)
        embed = discord.Embed(title=closest_color(r, g, b), color=color)
        embed.add_field(name="Decimal", value=color)
        embed.add_field(name="Hexadecimal", value=f"#{color:06X}")
        embed.add_field(name="RGB", value=f"{floor(r * 255)}, {floor(g * 255)}, {floor(b * 255)}")
        embed.add_field(name="CMYK", value=f"{floor(cmyk[0] * 100)}%, {floor(cmyk[1] * 100)}%, {floor(cmyk[2] * 100)}%, {floor(cmyk[3] * 100)}%")
        embed.add_field(name="HLS", value=f"{floor(hls[0] * 360)}\u00B0, {floor(hls[1] * 100)}%, {floor(hls[2] * 100)}%")
        embed.add_field(name="HSV", value=f"{floor(hsv[0] * 360)}\u00B0, {floor(hsv[1] * 100)}%, {floor(hsv[2] * 100)}%")
        embed.set_thumbnail(url=f"https://singlecolorimage.com/get/{color:06X}/64x64")
        await ctx.reply(embed=embed)

    @commands.command(aliases=["choose", "choices"])
    async def choice(self, ctx: commands.Context, *choices):
        """Make a choice for you"""
        await ctx.reply(random.choice(choices))

    @commands.command(aliases=["perm", "perms"])
    @commands.guild_only()
    async def permissions(self, ctx: commands.Context, member: discord.Member = None):
        """See a member's permissions"""
        if member is None:
            member = ctx.author
        permissions = ctx.channel.permissions_for(member)
        y = ""
        n = ""
        for perm, value in permissions:
            if value:
                y += f"+ {perm}\n"
            else:
                n += f"- {perm}\n"
        embed = discord.Embed(color=member.color)
        embed.set_author(name=member.name, icon_url=member.display_avatar.url)
        embed.add_field(name="Enabled", value=f"```diff\n{y}```")
        embed.add_field(name="Disabled", value=f"```diff\n{n}```")
        embed.set_footer(text=permissions.value)
        await ctx.reply(embed=embed)

    @commands.command(aliases=["activities", "playing", "game", "games"])
    @commands.guild_only()
    async def activity(self, ctx: commands.Context):
        """Show popular activities"""
        activities_dict = {}
        l = 0
        for m in ctx.guild.members:
            if m.bot:
                continue
            for activity in m.activities:
                if activity.type != ActivityType.playing:
                    continue
                l += 1
                if activity.name not in activities_dict:
                    activities_dict[activity.name] = 0
                activities_dict[activity.name] += 1
        top_activities = sorted(activities_dict.items(), key=lambda item: item[1], reverse=True)[:10]
        embed = discord.Embed(color=ctx.guild.owner.color)
        embed.set_author(
            name=ctx.guild.name,
            icon_url=ctx.guild.icon if ctx.guild.icon.url else None,
        )
        embed.set_footer(text=f"{l} activities")
        i = 1
        for a, b in top_activities:
            embed.add_field(name=f"{i}. {a}", value=b, inline=False)
            i += 1
        await ctx.reply(embed=embed)

    @commands.command(aliases=["msg", "message"])
    @commands.guild_only()
    async def quote(self, ctx: commands.Context, message: discord.Message):
        """Quote a message"""
        embed = discord.Embed(
            description=message.content,
            color=message.author.color,
            timestamp=message.created_at,
        )
        embed.set_author(
            name=format_username(message.author),
            icon_url=message.author.display_avatar.url,
        )
        await ctx.reply(embed=embed)

    @commands.group()
    @commands.guild_only()
    async def tag(self, ctx: commands.Context):
        """Use a tag"""
        if ctx.invoked_subcommand:
            return

    @tag.command()
    async def create(self, ctx: commands.Context):
        """Create a tag"""

    @tag.command()
    async def delete(self, ctx: commands.Context, tag_name):
        """Delete a tag"""


async def setup(bot):
    await bot.add_cog(Utility(bot))
