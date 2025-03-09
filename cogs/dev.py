import discord
from discord.ext import commands
from tortoise import Tortoise


class Developer(commands.Cog):
    """Commands for development purposes."""
    help_emoji = "\N{DESKTOP COMPUTER}"
    help_color = 0x4885cf

    @commands.command(aliases=["models", "redis"])
    @commands.is_owner()
    async def db(self, ctx: commands.Context):
        """Get database information"""
        memory = ctx.bot.redis.info("memory")
        color = int(ctx.bot.config["bot"]["color"], 16)
        redis_embed = discord.Embed(color=color)
        redis_embed.set_author(name="Redis", icon_url="https://avatars.githubusercontent.com/u/1529926")
        redis_embed.add_field(name="Used Memory", value=memory["used_memory_human"])
        redis_embed.add_field(name="Total System Memory", value=memory["total_system_memory_human"])
        redis_embed.add_field(name="Used Memory RSS", value=memory["used_memory_rss_human"])
        redis_embed.set_footer(text=f"{ctx.bot.redis.dbsize()} dbsize")
        models_embed = discord.Embed(color=color)
        models_embed.set_author(name="Models", icon_url="https://www.postgresql.org/media/img/about/press/elephant.png")
        total = 0
        for model in Tortoise.apps["models"].values():
            count = await model.all().count()
            total += count
            models_embed.add_field(name=model.__name__, value=count)
        models_embed.set_footer(text=f"{total} object{"" if total == 1 else "s"}")
        await ctx.reply(embeds=[redis_embed, models_embed])


async def setup(bot):
    await bot.add_cog(Developer(bot))
