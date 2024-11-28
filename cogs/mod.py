import asyncio
import datetime
import discord
from discord.ext import commands
import re


def parse_time(time, delta=True):
    time_units = {
        "d": 86400,
        "h": 3600,
        "m": 60,
        "s": 1,
    }
    pattern = r"(\d+)([dhms])"
    matches = re.findall(pattern, time)
    seconds = sum(int(n) * time_units[u] for n, u in matches)
    if delta:
        return datetime.timedelta(seconds=seconds)
    return seconds


class Moderation(commands.Cog):
    @commands.command()
    @commands.bot_has_permissions(kick_members=True)
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason = None):
        """Kick a member from the server"""
        await member.kick(reason=reason)
        await ctx.reply(f":white_check_mark: Kicked {member.name}.")

    @commands.command()
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def ban(self, ctx: commands.Context, user: discord.User, *, reason = None):
        """Ban a member from the server"""
        await ctx.guild.ban(user, reason=reason)
        await ctx.reply(f":white_check_mark: Banned {member.name}.")

    @commands.command()
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def multiban(self, ctx: commands.Context, *users: discord.User):
        """Ban multiple members from the server"""
        n = len(users)
        s = "" if n == 1 else "s"
        if not confirm:
            return await confirm.respond(":x: Operation aborted.")
        response = await confirm.respond(f":hourglass: Banning **{n}** member{s}...")
        for user in users:
            try:
                await ctx.guild.ban(user)
            except discord.HTTPException:
                pass
        await response.edit(content=f":white_check_mark: Banned **{n}** member{s}.")

    @commands.command()
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def massban(self, ctx: commands.Context, *, reason = None):
        """Ban suspicious members from the server"""
        now = datetime.datetime.now(datetime.timezone.utc)
        members = []
        for member in ctx.guild.members:
            if member.bot or member.guild_permissions.ban_members:
                continue
            conditions = 0
            if member.public_flags.spammer:
                conditions += 2
            if member.avatar == None:
                conditions += 1
            if re.search(r"\d{5,}$", member.name):
                conditions += 1
            if now - member.created_at < datetime.timedelta(days=7):
                conditions += 1
                if len(member.roles) < 2:
                    conditions += 1
            if now - member.joined_at < datetime.timedelta(hours=24):
                conditions += 1
                if ctx.guild.premium_subscriber_role in member.roles:
                    conditions += 2
            if conditions > 3:
                members.append(member)
        n = len(members)
        if n == 0:
            return await ctx.reply(":detective: No members detected.")
        s = "" if n == 1 else "s"
        c = "Too many members to list." if n > 20 else "\n".join([f"{m.name} ({m.id})" for m in members])
        confirm = await ctx.confirm(delete=True, content=f"```\n{c}\n```\n\n:question: Ban **{n}** member{s}? [y/n]")
        if not confirm:
            return await confirm.respond(":x: Operation aborted.")
        response = await confirm.respond(f":hourglass: **{n}** member{s}...")
        await ctx.guild.bulk_ban(members, reason=reason)
        await response.edit(content=f":white_check_mark: Banned **{n}** member{s}.")

    @commands.command()
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def softban(self, ctx: commands.Context, member: discord.Member, *, reason = None):
        """Softban a member from the server"""
        await member.ban(reason=reason)
        await member.unban(reason=reason)
        await ctx.reply(f":white_check_mark: Softbanned {member.name}.")

    @commands.command()
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def unban(self, ctx: commands.Context, user: discord.User, *, reason = None):
        """Unban a user from the server"""
        await ctx.guild.unban(user, reason=reason)
        await ctx.reply(f":white_check_mark: Unbanned {user.name}.")

    @commands.command(aliases=["timeout"])
    @commands.bot_has_permissions(moderate_members=True)
    @commands.has_permissions(moderate_members=True)
    @commands.guild_only()
    async def mute(self, ctx: commands.Context, member: discord.Member, until, *, reason = None):
        """Mute a member"""
        await member.timeout(parse_time(until), reason=reason)
        await ctx.reply(f":white_check_mark: Timed out {member.name}.")

    @commands.command()
    @commands.bot_has_permissions(moderate_members=True)
    @commands.has_permissions(moderate_members=True)
    @commands.guild_only()
    async def unmute(self, ctx: commands.Context, member: discord.Member, *, reason = None):
        """Unmute a member"""
        await member.timeout(None, reason=reason)
        await ctx.reply(f":white_check_mark: Removed timeout for {member.name}.")

    @commands.command()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def clear(self, ctx: commands.Context, limit = 100, *, reason = None):
        """Clear messages from a channel"""
        s = "" if limit == 1 else "s"
        confirm = await ctx.confirm(delete=False, content=f":question: Delete **{limit}** message{s}? [y/n]")
        if not confirm:
            await confirm.question.delete()
            confirm.question = None
            return await confirm.respond(":x: Operation aborted.")
        await ctx.channel.delete_messages([ctx.message, confirm.question, confirm.answer], reason=reason)
        await ctx.channel.purge(limit=limit, reason=reason)
        await ctx.send(content=f":white_check_mark: Deleted **{limit}** message{s}.", delete_after=5)

    @commands.command()
    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(manage_channels=True)
    @commands.guild_only()
    async def lock(self, ctx: commands.Context, *, reason = None):
        """Lock the channel"""
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        if not overwrite.send_messages:
            return
        overwrite.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite, reason=reason)
        await ctx.reply(f":lock: Locked {ctx.channel.name}.")

    @commands.command()
    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(manage_channels=True)
    @commands.guild_only()
    async def unlock(self, ctx: commands.Context, *, reason = None):
        """Unlock the channel"""
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        if overwrite.send_messages:
            return
        overwrite.send_messages = True
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite, reason=reason)
        await ctx.reply(f":key: Unlocked {ctx.channel.name}.")

    @commands.command()
    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(manage_channels=True)
    @commands.guild_only()
    async def slowmode(self, ctx: commands.Context, delay = None, *, reason = None):
        """Enable slowmode for the channel"""
        if delay != None:
            slowmode_delay = parse_time(delay, False)
        else:
            slowmode_delay = 5 if ctx.channel.slowmode_delay == 0 else 0
        await ctx.channel.edit(slowmode_delay=slowmode_delay, reason=reason)
        if slowmode_delay == 0:
            await ctx.reply(f":wind_blowing_face: Disabled slowmode for {ctx.channel.name}.")
        else:
            await ctx.reply(f":snail: Set slowmode for {ctx.channel.name} to {slowmode_delay}s.")

    @commands.command()
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(manage_roles=True)
    @commands.guild_only()
    async def addrole(self, ctx: commands.Context, member: discord.Member, role: discord.Role, *, reason = None):
        """Add a role to a member"""
        await member.add_roles(role, reason=reason)
        await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")

    @commands.command()
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(manage_roles=True)
    @commands.guild_only()
    async def removerole(self, ctx: commands.Context, member: discord.Member, role: discord.Role, *, reason = None):
        """Remove a role from a member"""
        await member.remove_roles(role, reason=reason)
        await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")

    @commands.command()
    @commands.bot_has_permissions(manage_nicknames=True)
    @commands.has_permissions(manage_nicknames=True)
    @commands.guild_only()
    async def nick(self, ctx: commands.Context, member: discord.Member, *, nick):
        """Set a member's nickname"""
        await member.edit(nick=nick)
        await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")

    @commands.command()
    @commands.bot_has_permissions(manage_nicknames=True)
    @commands.has_permissions(manage_nicknames=True)
    @commands.guild_only()
    async def clearnick(self, ctx: commands.Context, member: discord.Member):
        """Clear a member's nickname"""
        await member.edit(nick=None)
        await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")

    @commands.command()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def pin(self, ctx: commands.Context, message: discord.Message, *, reason = None):
        """Pin a message"""
        await message.pin(reason=reason)
        await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")

    @commands.command()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def unpin(self, ctx: commands.Context, message: discord.Message, *, reason = None):
        """Unpin a message"""
        await message.unpin(reason=reason)
        await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")

    @commands.command()
    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(manage_channels=True)
    @commands.guild_only()
    async def restrict(self, ctx: commands.Context, *, reason = None):
        """Restrict a channel to messages only"""
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        if overwrite.send_polls == False:
            return
        overwrite.update(
            add_reactions=False,
            attach_files=False,
            embed_links=False,
            send_polls=False,
        )
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite, reason=reason)
        await ctx.reply(f":lock: Enabled restrictions for {ctx.channel.name}.")

    @commands.command()
    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(manage_channels=True)
    @commands.guild_only()
    async def unrestrict(self, ctx: commands.Context, *, reason = None):
        """Unrestrict the channel"""
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        if overwrite.send_polls != False:
            return
        overwrite.update(
            add_reactions=None,
            attach_files=None,
            embed_links=None,
            send_polls=None,
        )
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite, reason=reason)
        await ctx.reply(f":unlock: Disabled restrictions for {ctx.channel.name}.")


async def setup(bot):
    await bot.add_cog(Moderation(bot))
