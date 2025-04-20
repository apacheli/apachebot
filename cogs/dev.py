from datetime import datetime

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
        redis_embed = discord.Embed(color=0xff4438)
        redis_embed.set_author(name="Redis", icon_url="https://avatars.githubusercontent.com/u/1529926")
        redis_embed.add_field(name="Used Memory", value=memory["used_memory_human"])
        redis_embed.add_field(name="Total System Memory", value=memory["total_system_memory_human"])
        redis_embed.add_field(name="Used Memory RSS", value=memory["used_memory_rss_human"])
        redis_embed.set_footer(text=f"{ctx.bot.redis.dbsize()} dbsize")
        models_embed = discord.Embed(color=0x31648c)
        models_embed.set_author(name="Models", icon_url="https://www.postgresql.org/media/img/about/press/elephant.png")
        total = 0
        for model in Tortoise.apps["models"].values():
            count = await model.all().count()
            total += count
            models_embed.add_field(name=model.__name__, value=count)
        models_embed.set_footer(text=f"{total} object{"" if total == 1 else "s"}")
        await ctx.reply(embeds=[redis_embed, models_embed])

    @commands.command(aliases=["id"])
    async def snowflake(self, ctx: commands.Context, snowflake: int):
        """Show snowflake information"""
        timestamp = (snowflake >> 22) + 1420070400000
        internal_worker_id = (snowflake & 0x3E0000) >> 17
        internal_process_id = (snowflake & 0x1F000) >> 12
        increment = snowflake & 0xFFF
        embed = discord.Embed(
            color=timestamp % 0xFFFFFF,
            description=bin(snowflake)[2:],
            title=snowflake,
            timestamp=datetime.fromtimestamp(timestamp / 1000),
        )
        embed.add_field(name="Internal Worker ID", value=internal_worker_id)
        embed.add_field(name="Internal Process ID", value=internal_process_id)
        embed.add_field(name="Increment", value=increment)
        embed.set_footer(text=timestamp)
        await ctx.reply(embed=embed)

    @commands.command(aliases=["history"])
    async def git(self, ctx: commands.Context):
        """Show commit history"""
        await ctx.reply("this doesn't do anything yet")


async def setup(bot):
    await bot.add_cog(Developer(bot))
