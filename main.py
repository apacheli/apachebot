import asyncio
import asyncpg
import configparser
from enum import Enum
import datetime
import discord
from discord.ext import commands
from discord.ui import Button, button, View
import os
import psutil
import re
import redis
from tortoise import Tortoise

from models.guild_config import GuildConfig


cogs = (
    "dev",
    "fun",
    "mod",
    "util",
)

activity_types = {
    "playing": discord.ActivityType.playing,
    "streaming": discord.ActivityType.streaming,
    "listening": discord.ActivityType.listening,
    "watching": discord.ActivityType.watching,
    "custom": discord.ActivityType.custom,
    "competing": discord.ActivityType.competing,
}


async def send_messages_check(ctx: commands.Context):
    return True
    if ctx.guild == None:
        return True
    permissions = ctx.channel.permissions_for(ctx.guild.me)
    return permissions.send_messages and permissions.read_message_history or permissions.add_reactions


class HelpPaginator(View):
    def __init__(self, ctx, mapping):
        super().__init__()
        self.ctx = ctx
        self.limit = len(mapping)
        self.keys = list(mapping)
        self.index = 0
        self.mapping = mapping
        self.update()

    def update(self):
        self.left.disabled = self.index == 0
        self.display_index.label = f"{self.index + 1}/{self.limit}"
        self.right.disabled = self.index == self.limit - 1

    def embed(self):
        category = self.keys[self.index]
        commands = self.mapping[category]
        embed = discord.Embed()
        embed.add_field(name="Commands", value=" ".join([f"`{command.name}`" for command in commands]))
        if category:
            embed.title = f"{category.emoji} {category.qualified_name}"
            embed.description = category.description
            embed.color = category.color
        embed.set_footer(text=f"{len(commands)} commands")
        return embed

    async def on_send(self):
        await self.ctx.send(embed=self.embed(), view=self)

    async def on_interaction(self, interaction: discord.Interaction):
        self.update()
        await interaction.response.edit_message(embed=self.embed(), view=self)

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == self.ctx.author.id

    @button(style=discord.ButtonStyle.primary, emoji="\N{BLACK LEFT-POINTING TRIANGLE}")
    async def left(self, interaction: discord.Interaction, _):
        self.index -= 1
        await self.on_interaction(interaction)

    @button(style=discord.ButtonStyle.secondary, disabled=True)
    async def display_index(self, interaction: discord.Interaction, btn):
        pass

    @button(style=discord.ButtonStyle.primary, emoji="\N{BLACK RIGHT-POINTING TRIANGLE}")
    async def right(self, interaction: discord.Interaction, _):
        self.index += 1
        await self.on_interaction(interaction)


class Help(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        await HelpPaginator(self.context, mapping).on_send()


class Confirmation:
    def __init__(self, ctx: commands.Context, question: discord.Message = None, answer: discord.Message = None):
        self.ctx = ctx
        self.question = question
        self.answer = answer

    def __bool__(self):
        return self.answer != None and self.answer.content in ("y", "yes")

    async def respond(self, *args, **kwargs):
        if self.answer:
            return await self.answer.reply(*args, **kwargs)
        if self.question:
            return await self.question.reply(*args, **kwargs)
        return await self.ctx.reply(*args, **kwargs)


class ApacheContext(commands.Context):
    async def confirm(self, delete = True, timeout = 60.0, *args, **kwargs):
        question = await self.reply(*args, **kwargs)
        def check(message: discord.Message):
            if message.author != self.author:
                return False
            return message.content.lower() in ("y", "yes", "n", "no")
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
    def __init__(self, config, redis):
        self.config = config
        self.redis = redis
        self.ready_at = None
        self.process = psutil.Process()
        activity_name = config["activity"]["name"]
        activity_type = activity_types[config["activity"]["type"]]
        activity = discord.Activity(
            name="Custom Status" if discord.ActivityType == discord.ActivityType.custom else activity_name,
            type=activity_type,
            url=config["activity"]["url"] if activity_type == discord.ActivityType.streaming else None,
            state=activity_name if activity_type == discord.ActivityType.custom else None,
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
        self.add_check(send_messages_check)

    async def on_ready(self):
        self.ready_at = datetime.datetime.now()

    async def get_context(self, message, *, cls = ApacheContext):
        return await super().get_context(message, cls=cls)

    async def on_command_error(self, ctx: commands.Context, error):
        await super().on_command_error(ctx, error)
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.reply(f":x: I am missing permissions:\n\n- `{"\n- `".join(error.missing_permissions)}`")

    async def start(self):
        discord.utils.setup_logging()
        for cog in cogs:
            await self.load_extension(f"cogs.{cog}")
        async with self:
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
        modules={"models": ["models.guild_config"]},
    )
    await Tortoise.generate_schemas()
    r = redis.Redis(
        host=config["redis"]["host"] or os.getenv("REDIS_HOST"),
        port=config["redis"]["port"] or os.getenv("REDIS_PORT"),
        db=0,
        decode_responses=True,
    )
    bot = Apachengine(config=config, redis=r)
    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
