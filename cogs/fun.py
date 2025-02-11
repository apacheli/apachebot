import aiohttp
import asyncio
import discord
from discord.ext import commands
from discord.ui import button, Button, Modal, TextInput, View
import json


class ThinkView(View):
    def __init__(self, think):
        super().__init__(timeout=None)
        self.think = think or "No thoughts..."

    @button(label="See Thoughts", style=discord.ButtonStyle.gray, emoji="\N{THOUGHT BALLOON}")
    async def think_button(self, interaction: discord.Interaction, _):
        await interaction.response.send_message(content=self.think, ephemeral=True)


def parse_message(message):
    end_think = message.find("</think>")
    return message[7:end_think].strip(), message[end_think + 8:].strip()


class Entertainment(commands.Cog):
    emoji = "\N{VIDEO GAME}"
    description = "Entertainment commands."
    color = 0x5cc433

    @commands.command(aliases=["deepseek"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ai(self, ctx: commands.Context):
        ollama = ctx.bot.config["ollama"]
        messages = []
        async for message in ctx.history(limit=int(ollama["history"])):
            messages.append({
                "role": "assistant" if message.author.id == ctx.bot.user.id else "user",
                "content": message.content,
            })
        messages.reverse()
        body = {
            "model": ctx.bot.config["ollama"]["model"],
            "messages": messages,
            "stream": False,
        }
        to_edit = await ctx.reply(f":hourglass: Coming up with something creative...")
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
            try:
                url = f"http://{ollama["host"]}:{ollama["port"]}/api/chat"
                async with session.post(url, json=body) as response:
                    data = await response.json()
                    print(data)
                    think, reply = parse_message(data["message"]["content"])
                    await to_edit.edit(content=reply, view=ThinkView(think))
            except asyncio.TimeoutError:
                await to_edit.edit(content=":x: Took too long to respond. Please try again!")


async def setup(bot):
    await bot.add_cog(Entertainment(bot))
