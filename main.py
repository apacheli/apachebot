import asyncio
import configparser
from enum import Enum
import discord
from discord.ext import commands
import os

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

class Confirmation:
    def __init__(self, ctx: commands.Context, question: discord.Message, answer: discord.Message):
        self.ctx = ctx
        self.question = question
        self.answer = answer

    def __bool__(self):
        if self.answer == None:
            return False
        return self.answer.content == "y"

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
            content = message.content.lower()
            return content == "y" or content == "n"

        try:
            answer = await self.bot.wait_for("message", check=check, timeout=timeout)
            if delete:
                await question.delete()
                return Confirmation(self, None, answer)
            return Confirmation(self, question, answer)
        except asyncio.TimeoutError:
            if delete:
                await question.delete()
                return Confirmation(self, None, None)
            return Confirmation(self, question, None)


class Apachengine(commands.AutoShardedBot):
    def __init__(self):
        config = configparser.ConfigParser()
        config.read("config.ini")
        self.config = config
        activity_name = config["activity"]["name"]
        activity_type = activity_types[config["activity"]["type"]]
        activity = discord.Activity(
            name="Custom Status" if discord.ActivityType == discord.ActivityType.custom else activity_name,
            type=activity_type,
            url=config["activity"]["url"] if activity_type == discord.ActivityType.streaming else None,
            state=activity_name if activity_type == discord.ActivityType.custom else None
        )
        allowed_mentions = discord.AllowedMentions.none()
        intents = discord.Intents.all()
        super().__init__(
            activity=activity,
            allowed_mentions=allowed_mentions,
            command_prefix=commands.when_mentioned_or(config["bot"]["command_prefix"]),
            enable_debug_events=True,
            #help_command=None,
            intents=intents,
            status=config["bot"]["status"],
        )

    async def get_context(self, message, *, cls = ApacheContext):
        return await super().get_context(message, cls=cls)

    async def start(self):
        discord.utils.setup_logging()
        for cog in cogs:
            await self.load_extension(f"cogs.{cog}")
        async with self:
            await super().start(self.config["bot"]["bot_token"])

    async def on_command_error(self, ctx: commands.Context, error):
        await super().on_command_error(ctx, error)
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.reply(f":x: I am missing permissions:\n\n- {"\n- ".join(error.missing_permissions)}")

def main():
    bot = Apachengine()
    asyncio.run(bot.start())


if __name__ == "__main__":
    main()
