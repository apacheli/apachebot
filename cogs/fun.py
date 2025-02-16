import aiohttp
import asyncio
import discord
from discord.ext import commands
from discord.ui import button, Button, Modal, TextInput, View
import json


class ThinkView(View):
    def __init__(self, think):
        super().__init__(timeout=None)
        self.think = think or "..."

    @button(label="See Thoughts", style=discord.ButtonStyle.gray, emoji="\N{THOUGHT BALLOON}")
    async def think_button(self, interaction: discord.Interaction, _):
        await interaction.response.send_message(self.think, ephemeral=True)


def parse_message(message):
    end_think = message.find("</think>")
    return message[7:end_think].strip(), message[end_think + 8:].strip()


class Entertainment(commands.Cog):
    emoji = "\N{VIDEO GAME}"
    description = "Entertainment commands."
    color = 0x5cc433

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    @commands.guild_only()
    async def ai(self, ctx: commands.Context, *, prompt):
        """Ask the AI something."""
        ollama = ctx.bot.config["ollama"]
        body = {
            "model": ollama["model"],
            "prompt": prompt,
            "stream": False,
        }
        url = f"http://{ollama["host"]}:{ollama["port"]}/api/generate"
        message = await ctx.reply(f":hourglass: Coming up with something creative...")
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
            try:
                async with session.post(url, json=body) as response:
                    data = await response.json()
                    think, reply = parse_message(data["response"])
                    await message.edit(content=reply, view=ThinkView(think))
            except asyncio.TimeoutError:
                await message.edit(content=":x: Took too long to respond. Please try again!")


async def setup(bot):t
    await bot.add_cog(Entertainment(bot))
