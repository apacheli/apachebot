import asyncio
import configparser
import datetime
import inspect
import os
import re
import psutil

import discord
from discord import ActivityType, ChannelType
from discord.ext import commands
import redis
from tortoise import Tortoise

from apacheutil import EmbedPaginator
from models.guild_config import GuildConfig


cogs = (
    "dev",
    "fun",
    "mod",
    "util",
)
cwd_len = len(os.getcwd())

activity_types = {
    "playing": ActivityType.playing,
    "streaming": ActivityType.streaming,
    "listening": ActivityType.listening,
    "watching": ActivityType.watching,
    "custom": ActivityType.custom,
    "competing": ActivityType.competing,
}


async def send_messages_check(ctx: commands.Context):
    if ctx.guild is None:
        return True
    permissions = ctx.channel.permissions_for(ctx.guild.me)
    if ctx.channel.type in (ChannelType.news_thread, ChannelType.public_thread, ChannelType.private_thread):
        return permissions.send_messages_in_threads
    return permissions.send_messages


class Help(commands.HelpCommand):
    def get_bot_mapping(self):
        mapping = [[cog, cog.get_commands()] for cog in self.context.bot.cogs.values()]
        embeds = []
        for cog, cog_commands in mapping:
            embed = discord.Embed(
                title=f"{cog.help_emoji} {cog.qualified_name}",
                description=cog.description,
                color=cog.help_color,
            )
            embed.add_field(
                name="Commands",
                value=" ".join(f"`{command.name}`" for command in cog_commands),
            )
            embed.set_footer(text=f"{len(cog_commands)} commands")
            embeds.append(embed)
        return mapping, embeds

    async def send_bot_help(self, mapping, /):
        paginator = EmbedPaginator(self.context, mapping[1])
        await paginator.start()

    async def send_cog_help(self, cog: commands.Cog, /):
        mapping, embeds = self.get_bot_mapping()
        paginator = EmbedPaginator(self.context, embeds, index=mapping[1].index(cog))
        await paginator.start()

    async def send_command_help(self, command: commands.Command, /):
        if not command.parent:
            return await self.context.reply(embed=self._get_help_command_embed(command))
        embeds = [self._get_help_command_embed(c) for c in command.parent.commands]
        embeds.insert(0, self._get_help_group_embed(command.parent))
        index = 1
        for c in command.parent.commands:
            if command is c:
                break
            index += 1
        await EmbedPaginator(self.context, embeds, index).start()

    async def send_group_help(self, group: commands.Group, /):
        embeds = [self._get_help_command_embed(c) for c in group.commands]
        embeds.insert(0, self._get_help_group_embed(group))
        await EmbedPaginator(self.context, embeds).start()

    def _get_help_group_embed(self, group: commands.Group):
        embed = discord.Embed(
            title=group.qualified_name,
            description=f"{group.short_doc}\n```\n{"\n".join(self.get_command_signature(c) for c in group.commands)}\n```",
            color=group.cog.help_color,
        )
        embed.add_field(name="Source", value=self._get_command_source(group))
        embed.set_footer(text=f"{group.cog.help_emoji} {group.cog.qualified_name}")
        return embed

    def _get_help_command_embed(self, command: commands.Command):
        embed = discord.Embed(
            title=command.qualified_name,
            description=f"{command.short_doc}\n```\n{self.get_command_signature(command)}\n```",
            color=command.cog.help_color,
        )
        embed.add_field(name="Source", value=self._get_command_source(command))
        embed.set_footer(text=f"{command.cog.help_emoji} {command.cog.qualified_name}")
        return embed

    def _get_command_source(self, command: commands.Command):
        # https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/meta.py#L405-L446
        if command.name == "help":
            code = Help
            filename = "/main.py"
        else:
            code = command.callback.__code__
            filename = code.co_filename[cwd_len:].replace("\\", "/")
        lines, firstlineno = inspect.getsourcelines(code)
        return f"https://github.com/apacheli/apachebot/tree/master{filename}#L{firstlineno}-L{firstlineno + len(lines) - 1}"


class Confirmation:
    def __init__(self, ctx: commands.Context, question: discord.Message = None, answer: discord.Message = None):
        self.ctx = ctx
        self.question = question
        self.answer = answer

    def __bool__(self):
        return self.answer != None and self.answer.content in ("y", "yes", "true", "1")

    async def respond(self, *args, **kwargs):
        if self.answer:
            await self.answer.reply(*args, **kwargs)
        elif self.question:
            await self.question.reply(*args, **kwargs)
        else:
            await self.ctx.reply(*args, **kwargs)


class ApacheContext(commands.Context):
    async def confirm(self, *args, delete = True, timeout = 60.0, **kwargs):
        question = await self.reply(*args, **kwargs)
        def check(message: discord.Message):
            if message.author != self.author:
                return False
            return message.content.lower() in ("y", "yes", "n", "no", "true", "false", "1", "0")
        try:
            answer = await self.bot.wait_for("message", check=check, timeout=timeout)
            if delete:
                await question.delete()
                return Confirmation(self, answer=answer)
            return Confirmation(self, question, answer)
        except asyncio.TimeoutError:
            if delete:
                await question.delete()
                return Confirmation(self)
            return Confirmation(self, question=question)


class Apachengine(commands.AutoShardedBot):
    def __init__(self, config, r):
        self.config = config
        self.version = "4.0.1"
        self.redis = r
        self.ready_at = 0
        self.process = psutil.Process()
        activity_name = config["activity"]["name"]
        activity_type = activity_types[config["activity"]["type"]]
        activity = discord.Activity(
            name="Custom Status" if ActivityType == ActivityType.custom else activity_name,
            type=activity_type,
            url=config["activity"]["url"] if activity_type == ActivityType.streaming else None,
            state=activity_name if activity_type == ActivityType.custom else None,
        )
        allowed_mentions = discord.AllowedMentions.none()
        intents = discord.Intents.all()
        super().__init__(
            activity=activity,
            allowed_mentions=allowed_mentions,
            command_prefix=commands.when_mentioned_or(config["bot"]["command_prefix"]),
            enable_debug_events=True,
            help_command=Help(),
            intents=intents,
            status=config["bot"]["status"],
        )

    async def on_ready(self):
        self.ready_at = datetime.datetime.now()

    async def get_context(self, message, *, cls = ApacheContext):
        return await super().get_context(message, cls=cls)

    async def on_command_error(self, ctx: commands.Context, error, /):
        await super().on_command_error(ctx, error)
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.reply(f":x: I am missing permissions:\n\n- `{"\n- `".join(error.missing_permissions)}`")

    async def start(self):
        discord.utils.setup_logging()
        for cog in cogs:
            await self.load_extension(f"cogs.{cog}")
        async with self:
            self.help_command.cog = self.get_cog("Utility")
            await super().start(self.config["bot"]["bot_token"] or os.getenv("BOT_TOKEN"))

    def parse_time(self, time, delta=True):
        time_units = {
            "d": 86400,
            "h": 3600,
            "m": 60,
            "s": 1,
        }
        pattern = r"(\d+)([dhms])"
        matches = re.findall(pattern, time)
        seconds = sum(int(n) * time_units[u] for n, u in matches)
        return datetime.timedelta(seconds=seconds) if delta else seconds

    async def get_guild_config(self, guild: discord.Guild):
        redis_name = f"guild_configs:{guild.id}"
        cached = self.redis.hgetall(redis_name)
        if cached:
            return GuildConfig(**cached)
        config = await GuildConfig.get_or_none(id=guild.id)
        if config:
            mapping = {k: v for k in config._meta.fields if (v := getattr(config, k)) != None}
            self.redis.hset(redis_name, mapping=mapping)
            self.redis.expire(redis_name, 86400)
            return config
        return GuildConfig(id=guild.id)

    async def update_guild_config(self, guild: discord.Guild, **kwargs):
        redis_name = f"guild_configs:{guild.id}"
        if self.redis.exists(redis_name):
            self.redis.hset(redis_name, mapping=kwargs)
        await GuildConfig.update_or_create(id=guild.id, defaults=kwargs)
        # Return a fake object because it's not worth making two requests
        return GuildConfig(**kwargs)


async def main():
    config = configparser.ConfigParser()
    config.read("config.local.ini")
    user = config["db"]["user"] or os.getenv("DB_USER")
    password = config["db"]["password"] or os.getenv("DB_PASSWORD")
    database = config["db"]["database"] or os.getenv("DB_DATABASE")
    host = config["db"]["host"] or os.getenv("DB_HOST")
    port = config["db"]["port"] or os.getenv("DB_PORT")
    await Tortoise.init(
        db_url=f"postgres://{user}:{password}@{host}:{port}/{database}",
        modules={"models": ["models.guild_config", "models.guild_tag"]},
    )
    await Tortoise.generate_schemas()
    r = redis.Redis(
        host=config["redis"]["host"] or os.getenv("REDIS_HOST"),
        port=config["redis"]["port"] or os.getenv("REDIS_PORT"),
        db=0,
        decode_responses=True,
    )
    bot = Apachengine(config=config, r=r)
    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
