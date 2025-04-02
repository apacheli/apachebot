import discord
from discord.ui import button, View


def format_username(member: discord.Member):
    alt_name = member.nick or member.global_name
    tag_name = f"{member.name}{f"#{member.discriminator}" if member.discriminator != "0" else ""}"
    return f"{alt_name or tag_name}{f" ({tag_name})" if alt_name else ""}"


class EmbedPaginator(View):
    def __init__(self, ctx, embeds, index = 0):
        super().__init__()
        self.ctx = ctx
        self.embeds = embeds
        self.index = index
        self.limit = len(embeds)

    def update(self):
        self.left.disabled = self.rewind.disabled = self.index == 0
        self.display_index.label = f"{self.index + 1}/{self.limit}"
        self.right.disabled = self.forward.disabled = self.index == self.limit - 1

    async def start(self):
        self.update()
        await self.ctx.reply(embed=self.embeds[self.index], view=self)

    async def update_interaction(self, interaction: discord.Interaction):
        self.update()
        await interaction.response.edit_message(embed=self.embeds[self.index], view=self)

    async def interaction_check(self, interaction: discord.Interaction, /):
        return interaction.user.id == self.ctx.author.id

    @button(style=discord.ButtonStyle.primary, emoji="\N{BLACK LEFT-POINTING DOUBLE TRIANGLE}")
    async def rewind(self, interaction: discord.Interaction, _):
        self.index = 0
        await self.update_interaction(interaction)

    @button(style=discord.ButtonStyle.primary, emoji="\N{BLACK LEFT-POINTING TRIANGLE}")
    async def left(self, interaction: discord.Interaction, _):
        self.index -= 1
        await self.update_interaction(interaction)

    @button(style=discord.ButtonStyle.secondary, disabled=True)
    async def display_index(self, interaction: discord.Interaction, _):
        pass

    @button(style=discord.ButtonStyle.primary, emoji="\N{BLACK RIGHT-POINTING TRIANGLE}")
    async def right(self, interaction: discord.Interaction, _):
        self.index += 1
        await self.update_interaction(interaction)

    @button(style=discord.ButtonStyle.primary, emoji="\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE}")
    async def forward(self, interaction: discord.Interaction, _):
        self.index = self.limit - 1
        await self.update_interaction(interaction)
