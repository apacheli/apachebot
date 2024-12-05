import asyncio
import datetime
import discord
from discord.ext import commands
import math
import re


ONE_WEEK = datetime.timedelta(days=7)
ONE_DAY = datetime.timedelta(hours=24)


class Moderation(commands.Cog):
    def _rank_member_suspicion(self, ctx: commands.Context, member, now):
        if member.bot or member.guild_permissions.ban_members:
            return 0
        conditions = 0
        if member.public_flags.spammer:
            conditions += 3
        if member.avatar == None:
            conditions += 1
        if re.search(r"\d{5,}$", member.name):
            conditions += 1
        if now - member.created_at < ONE_WEEK:
            conditions += 1
        if now - member.joined_at < ONE_DAY:
            conditions += 1
            if member.premium_since != None:
                conditions += 1
        return conditions

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
        confirm = await ctx.confirm(delete=True, content=f"```\n{c}\n```\n\n:question: Ban **{n}** member{s}? [y/n]")
        if not confirm:
            return await confirm.respond(":x: Operation aborted.")
        await ctx.guild.bulk_ban(users)
        await ctx.reply(f":white_check_mark: Banned **{n}** member{s}.")

    @commands.command(aliases=["bulkban"])
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def massban(self, ctx: commands.Context, *, reason = None):
        """Ban suspicious members from the server"""
        now = datetime.datetime.now(datetime.timezone.utc)
        members = [m for m in ctx.guild.members if self._rank_member_suspicion(ctx, m, now) > 3]
        n = len(members)
        if n == 0:
            return await ctx.reply(":detective: No members detected.")
        s = "" if n == 1 else "s"
        c = "Too many members to list." if n > 25 else "\n".join([f"{m.name} ({m.id})" for m in members])
        confirm = await ctx.confirm(delete=True, content=f"```\n{c}\n```\n\n:question: Ban **{n}** member{s}? [y/n]")
        if not confirm:
            return await confirm.respond(":x: Operation aborted.")
        await ctx.guild.bulk_ban(members, reason=reason)
        await ctx.reply(f":white_check_mark: Banned **{n}** member{s}.")

    @commands.command(aliases=["suspicious"])
    @commands.guild_only()
    async def sus(self, ctx: commands.Context, user: discord.Member = None):
        """Show suspicious members in a server"""
        now = datetime.datetime.now(datetime.timezone.utc)
        if user:
            sus_rank = self._rank_member_suspicion(ctx, user, now)
            return await ctx.reply(f":detective: {user.name} has a suspicious ranking of **{sus_rank}**.")
        members = [m for m in ctx.guild.members if self._rank_member_suspicion(ctx, m, now) > 3]
        n = len(members)
        if n == 0:
            return await ctx.reply(":detective: No members detected.")
        c = "Too many members to list." if n > 25 else "\n".join([f"{m.name} ({m.id})" for m in members])
        await ctx.reply(f"```\n{c}\n```\n\n:detective: **{n}** member{"" if n == 1 else "s"} {"is" if n == 1 else "are"} suspicious.")

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
        if member.is_timed_out:
            return
        await member.timeout(ctx.bot.parse_time(until), reason=reason)
        await ctx.reply(f":white_check_mark: Timed out {member.name}.")

    @commands.command(aliases=["untimeout"])
    @commands.bot_has_permissions(moderate_members=True)
    @commands.has_permissions(moderate_members=True)
    @commands.guild_only()
    async def unmute(self, ctx: commands.Context, member: discord.Member, *, reason = None):
        """Unmute a member"""
        if not member.is_timed_out:
            return
        await member.timeout(None, reason=reason)
        await ctx.reply(f":white_check_mark: Removed timeout for {member.name}.")

    @commands.command(aliases=["purge"])
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

    @commands.command(aliases=["close"])
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

    @commands.command(aliases=["open"])
    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(manage_channels=True)
    @commands.guild_only()
    async def unlock(self, ctx: commands.Context, *, reason = None):
        """Unlock the channel"""
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        if overwrite.send_messages:
            return
        overwrite.send_messages = None
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite, reason=reason)
        await ctx.reply(f":key: Unlocked {ctx.channel.name}.")

    @commands.command()
    @commands.bot_has_permissions(manage_guild=True)
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def lockdown(self, ctx: commands.Context, until, *, reason = None):
        """Disable messages and invites"""
        if not ctx.guild.default_role.permissions.send_messages:
            return
        permissions = discord.Permissions(
            add_reactions=False,
            send_messages=False,
        )
        await ctx.guild.default_role.edit(permissions=permissions, reason=reason)
        delay = datetime.datetime.now(datetime.timezone.utc) + ctx.bot.parse_time(until, True)
        await ctx.guild.edit(
            dms_disabled_until=delay,
            invites_disabled=True,
            reason=reason,
        )
        await ctx.reply(f":warning: Lockdown active until <t:{math.floor(delay.timestamp())}>.")

    @commands.command(aliases=["lockup"])
    @commands.bot_has_permissions(manage_guild=True)
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def unlockdown(self, ctx: commands.Context, *, reason = None):
        """Disable the lockdown"""
        if ctx.guild.default_role.permissions.send_messages:
            return
        permissions = discord.Permissions(
            add_reactions=None,
            send_messages=None,
        )
        await ctx.guild.default_role.edit(permissions=permissions, reason=reason)
        await ctx.guild.edit(
            dms_disabled_until=None,
            invites_disabled=False,
            reason=reason,
        )
        await ctx.reply(":warning: Lockdown disabled.")

    @commands.command(aliases=["slow"])
    @commands.bot_has_permissions(manage_channels=True)
    @commands.has_permissions(manage_channels=True)
    @commands.guild_only()
    async def slowmode(self, ctx: commands.Context, delay = None, *, reason = None):
        """Enable slowmode for the channel"""
        if delay != None:
            slowmode_delay = ctx.bot.parse_time(delay, False)
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
        if member.nick == nick:
            return
        await member.edit(nick=nick)
        await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")

    @commands.command()
    @commands.bot_has_permissions(manage_nicknames=True)
    @commands.has_permissions(manage_nicknames=True)
    @commands.guild_only()
    async def clearnick(self, ctx: commands.Context, member: discord.Member):
        """Clear a member's nickname"""
        if member.nick == None:
            return
        await member.edit(nick=None)
        await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")

    @commands.command()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def pin(self, ctx: commands.Context, message: discord.Message, *, reason = None):
        """Pin a message"""
        if message.pinned:
            return
        await message.pin(reason=reason)
        await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")

    @commands.command()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def unpin(self, ctx: commands.Context, message: discord.Message, *, reason = None):
        """Unpin a message"""
        if not message.pinned:
            return
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
