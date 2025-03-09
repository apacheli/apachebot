import datetime
import discord
from discord.ext import commands
from discord.ui import button, Button, Modal, TextInput, View
import json
import math
import re
from string import Template


ONE_WEEK = datetime.timedelta(days=7)
ONE_MONTH = datetime.timedelta(days=30)


def _format(string, keys):
    return Template(string).safe_substitute(keys)


def _on_member_join_embed(config, member: discord.Member):
    guild = member.guild
    keys = {
        "user": member.global_name or member.name,
        "mention": member.mention,
        "avatar": member.display_avatar.url,
        "member_count": guild.member_count,
        "server": guild.name,
        "server_icon": guild.icon.url if guild.icon else "",
        "system_channel": guild.system_channel.mention if guild.system_channel else "",
        "rules_channel": guild.rules_channel.mention if guild.rules_channel else "",
    }
    embed = discord.Embed(
        description=_format(config.welcome_description, keys),
    )
    embed.set_author(
        name=_format(config.welcome_title, keys),
        icon_url=member.display_avatar.url,
    )
    embed.set_image(url=_format(config.welcome_image, keys))
    embed.set_footer(text=_format(config.welcome_footer, keys))
    return embed


def _rank_member_suspicion(_ctx: commands.Context, member, now):
    if member.bot or member.guild_permissions.ban_members:
        return 0
    conditions = 0
    if member.public_flags.spammer:
        conditions += 3
    if member.avatar == None:
        conditions += 1
    if re.search(r"\d{5,}$", member.name):
        conditions += 1
    if now - member.created_at < ONE_MONTH:
        conditions += 1
    if now - member.joined_at < ONE_WEEK:
        conditions += 1
    return conditions


class JoinLogConfigureModal(Modal):
    def __init__(self, view, previous_interaction: discord.Interaction, config):
        super().__init__(title=f"Configure Join Log for {view.ctx.guild.name}")
        self.channel = TextInput(
            label="Channel ID",
            placeholder="12345678901234567890",
            required=False,
            max_length=20,
            min_length=15,
            default=config.join_log,
        )
        self.welcome_title = TextInput(
            label="Welcome Title",
            placeholder="Hello, $user!",
            max_length=200,
            default=config.welcome_title,
        )
        self.welcome_description = TextInput(
            label="Welcome Description",
            style=discord.TextStyle.long,
            placeholder="Welcome to $server. Please read the rules over at $rules_channel.",
            required=False,
            max_length=1000,
            default=config.welcome_description,
        )
        self.welcome_image = TextInput(
            label="Welcome Image",
            placeholder="$avatar",
            required=False,
            max_length=200,
            default=config.welcome_image,
        )
        self.welcome_footer = TextInput(
            label="Welcome Footer",
            placeholder="$member_count members are in this server!",
            required=False,
            max_length=200,
            default=config.welcome_footer,
        )
        self.add_item(self.channel)
        self.add_item(self.welcome_title)
        self.add_item(self.welcome_description)
        self.add_item(self.welcome_image)
        self.add_item(self.welcome_footer)
        self.view = view
        self.previous_interaction = previous_interaction

    async def on_submit(self, interaction: discord.Interaction, /):
        channel = interaction.guild.get_channel(int(self.channel.value)) if self.channel.value.isdigit() else None
        if channel == None or channel.type != discord.ChannelType.text:
            return await interaction.response.send_message(":x: Invalid channel provided. Please try again.", ephemeral=True)
        _fake_config = await self.view.ctx.bot.update_guild_config(
            self.view.ctx.guild,
            join_log=channel.id,
            welcome_title=self.welcome_title.value.strip(),
            welcome_description=self.welcome_description.value.strip(),
            welcome_image=self.welcome_image.value.strip(),
            welcome_footer=self.welcome_footer.value.strip(),
        )
        await self.previous_interaction.edit_original_response(view=self.view)
        await interaction.response.send_message(
            f":white_check_mark: Set the join log to <#{channel.id}>. Your join log will look like this:",
            embed=_on_member_join_embed(_fake_config, interaction.user),
        )


class JoinLogConfigure(View):
    def __init__(self, ctx: commands.Context):
        super().__init__()
        self.ctx = ctx
        self.modal = None

    @button(style=discord.ButtonStyle.secondary, label="Configure", emoji="\N{GEAR}")
    async def configure(self, interaction: discord.Interaction, btn: Button):
        if self.modal == None:
            config = await self.ctx.bot.get_guild_config(self.ctx.guild)
            self.modal = JoinLogConfigureModal(self, interaction, config)
        await interaction.response.send_modal(self.modal)
        btn.disabled = True

    async def interaction_check(self, interaction: discord.Interaction, /):
        return interaction.user.id == self.ctx.author.id


class Moderation(commands.Cog):
    """Commands for server moderation. Only moderators can access these commands."""
    help_emoji = "\N{SHIELD}"
    help_color = 0x334bd4

    def __init__(self, bot: commands.AutoShardedBot):
        super().__init__()
        self.bot = bot

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
        await ctx.reply(f":white_check_mark: Banned {user.name}.")

    @commands.command()
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def multiban(self, ctx: commands.Context, *users: discord.User):
        """Ban multiple members from the server"""
        n = len(users)
        s = "" if n == 1 else "s"
        c = "Too many members to list." if n > 50 else "\n".join(f"{u.name} ({u.id})" for u in users)
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
        members = [m for m in ctx.guild.members if _rank_member_suspicion(ctx, m, now) > 3]
        n = len(members)
        if n == 0:
            return await ctx.reply(":detective: No members detected.")
        s = "" if n == 1 else "s"
        c = "Too many members to list." if n > 50 else "\n".join(f"{m.name} ({m.id})" for m in members)
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
            sus_rank = _rank_member_suspicion(ctx, user, now)
            return await ctx.reply(f":detective: {user.name} has a suspicious ranking of **{sus_rank}**.")
        members = [m for m in ctx.guild.members if _rank_member_suspicion(ctx, m, now) > 3]
        n = len(members)
        if n == 0:
            return await ctx.reply(":detective: No members detected.")
        c = "Too many members to list." if n > 50 else "\n".join(f"{m.name} ({m.id})" for m in members)
        await ctx.reply(f"```\n{c}\n```\n\n:detective: **{n}** member{" is" if n == 1 else "s are"} suspicious.")

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
        await member.timeout(self.bot.parse_time(until), reason=reason)
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
        delay = datetime.datetime.now(datetime.timezone.utc) + self.bot.parse_time(until, True)
        await ctx.guild.edit(
            dms_disabled_until=delay,
            invites_disabled=True,
            reason=reason,
        )
        await ctx.reply(f":warning: Lockdown active until <t:{math.floor(delay.timestamp())}>. Click **Report Raid** :shield: if there a raid.")

    @commands.command(aliases=["lockup"])
    @commands.bot_has_permissions(manage_guild=True)
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def unlockdown(self, ctx: commands.Context, *, reason = None):
        """Disable the lockdown"""
        if ctx.guild.default_role.permissions.send_messages:
            return
        permissions = discord.Permissions(
            add_reactions=True,
            send_messages=True,
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
            slowmode_delay = self.bot.parse_time(delay, False)
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
        if overwrite.add_reactions == False:
            return
        overwrite.update(
            add_reactions=False,
            attach_files=False,
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
        if overwrite.add_reactions != False:
            return
        overwrite.update(
            add_reactions=None,
            attach_files=None,
            send_polls=None,
        )
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite, reason=reason)
        await ctx.reply(f":unlock: Disabled restrictions for {ctx.channel.name}.")

    @commands.command(aliases=["guildconfig", "server_config", "serverconfig"])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def guild_config(self, ctx: commands.Context):
        """Show the server configuration"""
        config = await self.bot.get_guild_config(ctx.guild)
        await ctx.reply(f"```json\n{json.dumps(dict(config), indent=4)}\n```")

    @commands.command(aliases=["joinlog"])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def join_log(self, ctx: commands.Context):
        """Set the join log for this server"""
        config = await self.bot.get_guild_config(ctx.guild)
        if config.join_log:
            return await ctx.reply(f":speech_balloon: The join log for this server is <#{config.join_log}>.", view=JoinLogConfigure(ctx))
        return await ctx.reply(":speech_balloon: There is no join log for this server. Click **:gear: Configure** to get started.", view=JoinLogConfigure(ctx))

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if not member.guild.me.guild_permissions.manage_roles:
            return
        config = await self.bot.get_guild_config(member.guild)
        if config.join_log == None:
            return
        channel = self.bot.get_channel(config.join_log)
        if channel and channel.permissions_for(member.guild.me).send_messages:
            await channel.send(embed=_on_member_join_embed(config, member))


async def setup(bot):
    await bot.add_cog(Moderation(bot))
