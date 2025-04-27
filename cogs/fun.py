import aiohttp
from datetime import datetime
import json
from random import randint
import re
from urllib.parse import quote

import discord
from discord.ext import commands
from discord.ui import button, Modal, TextInput

from apacheutil import BaseView, EmbedPaginator, format_username


levels = (
    0,
    17.165605545043945,
    18.53504753112793,
    19.90485382080078,
    21.27490234375,
    22.6454,
    24.649612426757812,
    26.640642166137695,
    28.868587493896484,
    31.36768,
    34.14334487915039,
    37.201,
    40.66,
    44.4466667175293,
    48.56352,
    53.74848,
    59.0818977355957,
    64.4200439453125,
    69.72446,
    75.12314,
    80.58478,
    86.11203,
    91.70374,
    97.24463,
    102.8126449584961,
    108.40956,
    113.20169,
    118.1029052734375,
    122.97932,
    129.72732543945312,
    136.29291,
    142.6708526611328,
    149.02902,
    155.41699,
    161.8255,
    169.10631,
    176.51808,
    184.07274,
    191.70952,
    199.55691528320312,
    207.38205,
    215.3989,
    224.16566467285156,
    233.50216674804688,
    243.35057,
    256.0630798339844,
    268.5435,
    281.52606201171875,
    295.0136413574219,
    309.0672,
    323.6016,
    336.7575378417969,
    350.5303,
    364.4827,
    378.6191711425781,
    398.6004,
    416.39825439453125,
    434.387,
    452.9510498046875,
    472.6062316894531,
    492.8849,
    513.5685424804688,
    539.1032,
    565.5105590820312,
    592.5387573242188,
    624.4434,
    651.4701538085938,
    679.4968,
    707.7940673828125,
    736.6714477539062,
    765.6402587890625,
    794.7734,
    824.6773681640625,
    851.1578,
    877.7420654296875,
    914.2291,
    946.7467651367188,
    979.4114,
    1011.223,
    1044.791748046875,
    1077.4437,
    1109.99755859375,
    1142.9766,
    1176.3695,
    1210.1844482421875,
    1253.8357,
    1288.9527587890625,
    1325.4841,
    1363.4569,
    1405.0974,
    1446.8535,
    1488.2156,
    1528.4446,
    1580.3679,
    1630.8475,
    1711.19775390625,
    1780.454,
    1847.32275390625,
    1911.4744,
    1972.8644,
    2030.0718,
)

shields = (
    0,
    91.1791,
    98.7076644897461,
    106.23622,
    113.76477,
    121.29332,
    128.82188415527344,
    136.35042,
    143.8789825439453,
    151.4075164794922,
    158.93608,
    169.99148559570312,
    181.07625,
    192.19037,
    204.0482,
    215.939,
    227.8627471923828,
    247.68594360351562,
    267.5421,
    287.4312,
    303.826416015625,
    320.2252197265625,
    336.62762451171875,
    352.31927490234375,
    368.01092529296875,
    383.7025451660156,
    394.432373046875,
    405.18145751953125,
    415.9499206542969,
    426.7376403808594,
    437.5447,
    450.6,
    463.7003,
    476.8455810546875,
    491.1275,
    502.5545654296875,
    514.0121,
    531.4096,
    549.9796,
    568.5849,
    584.9965,
    605.6703491210938,
    626.3862,
    646.0523,
    665.7556,
    685.4961,
    700.8394,
    723.3331,
    745.8653,
    768.4357,
    786.7919311523438,
    809.5388,
    832.3290405273438,
    855.1626586914062,
    878.0396,
    899.4848,
    919.362,
    946.0396,
    974.7642,
    1003.5786,
    1030.077,
    1056.635,
    1085.2463,
    1113.9244,
    1149.2587,
    1178.0648,
    1200.2237548828125,
    1227.6603,
    1257.243,
    1284.9173583984375,
    1314.7529,
    1342.6652,
    1372.75244140625,
    1396.321,
    1427.3124,
    1458.3745,
    1482.3358,
    1511.9109,
    1541.5493,
    1569.1537,
    1596.8143,
    1622.4197,
    1648.074,
    1666.3761,
    1684.6782,
    1702.9803466796875,
    1726.1047,
    1754.6715,
    1785.8666,
    1817.137451171875,
    1851.0603,
    1885.0671,
    1921.7493,
    1958.5233,
    2006.1941,
    2041.569,
    2054.47216796875,
    2065.975,
    2174.72265625,
    2186.768310546875,
    2198.814,
)

emojis_bloons = {
    "STARTING_CLASH": "<:_:1266472607658545172>",
    "MAX_MONKEYS": "<:_:1266587052091375677>",
    "MAX_PARAGONS": "<:_:1266599391087558716>",
    "LIVES": "<:_:1266473058789621841>",
    "ROUNDS": "<:_:1266794545371414528>",
    "MAP": "<:_:1266797307299495968>",
    "ABILITY_COOLDOWN_INCREASE": "<:_:1266475019744313458>",
    "ABILITY_COOLDOWN_DECREASE": "<:_:1266475018720776242>",
    "REMOVABLE_COST_INCREASE": "<:_:1266482291211763803>",
    "REMOVABLE_COST_DECREASE": "<:_:1266482289785966793>",
    "REGROW_RATE_INCREASE": "<:_:1266587031262330880>",
    "REGROW_RATE_DECREASE": "<:_:1266587030045982834>",
    "BLOON_SPEED_INCREASE": "<:_:1266476443550879746>",
    "BLOON_SPEED_DECREASE": "<:_:1266587474939875328>",
    "MOAB_SPEED_INCREASE": "<:_:1266483982724235376>",
    "MOAB_SPEED_DECREASE": "<:_:1266483981503824044>",
    "BOSS_SPEED_INCREASE": "<:_:1266587877878534278>",
    "BOSS_SPEED_DECREASE": "<:_:1266587879002603610>",
    "CERAMIC_HP_INCREASE": "<:_:1266586881286738002>",
    "CERAMIC_HP_DECREASE": "<:_:1266586880334626847>",
    "MOAB_HP_INCREASE": "<:_:1266483985131896882>",
    "MOAB_HP_DECREASE": "<:_:1266483983684731003>",
    "BOSS_HP_INCREASE": "<:_:1266588226467135499>",
    "BOSS_HP_DECREASE": "<:_:1266588225799983166>"
}

rps_pretty = [
    ":moyai: **Rock**",
    ":newspaper: **Paper**",
    ":scissors: **Scissors**",
]

_roll_r = re.compile(r"^(?:(\d{1,2})d)?(\d{1,4})([+-]\d{1,4})?$")
_urban_r = pattern = re.compile(r"\[(.*?)\]")


def challenge_color(s):
    return 0x4694d5 if s.startswith("rot") else 0xea6334 if s.startswith("adv") else 0xff9600 if s.startswith("coop") else None


boss_thumbnails = {
    "bloonarius": "https://www.bloonswiki.com/images/2/27/BTD6_BloonariusPortrait.png",
    "bloonarius-elite": "https://www.bloonswiki.com/images/7/7f/BTD6_BloonariusPortraitElite.png",
    "lych": "https://www.bloonswiki.com/images/1/12/BTD6_LychPortrait.png",
    "lych-elite": "https://www.bloonswiki.com/images/8/8b/BTD6_LychPortraitElite.png",
    "vortex": "https://www.bloonswiki.com/images/8/89/BTD6_VortexPortrait.png",
    "vortex-elite": "https://www.bloonswiki.com/images/9/9a/BTD6_VortexPortraitElite.png",
    "dreadbloon": "https://www.bloonswiki.com/images/e/e4/BTD6_DreadbloonPortrait.png",
    "dreadbloon-elite": "https://www.bloonswiki.com/images/c/c7/BTD6_DreadbloonPortraitElite.png",
    "phayze": "https://www.bloonswiki.com/images/9/9a/BTD6_PhayzePortrait.png",
    "phayze-elite": "https://www.bloonswiki.com/File:BTD6_PhayzePortraitElite.png",
    "blastapopoulos": "https://www.bloonswiki.com/images/c/ce/BTD6_BlastapopoulosPortrait.png",
    "blastapopoulos-elite": "https://www.bloonswiki.com/images/a/a8/BTD6_BlastapopoulosPortraitElite.png",
}


def create_bloons_document(data, *, color = 0xFF0000, thumbnail = None):
    embed = discord.Embed(
        title=f"{data["name"]} | {data["difficulty"]} - {data["mode"]}",
        color=color,
    )
    embed.add_field(name=f"{emojis_bloons["STARTING_CLASH"]} Starting Cash", value=data["startingCash"])
    embed.add_field(name=f"{emojis_bloons["LIVES"]} Lives", value=f"{data["lives"]}/{data["maxLives"]}")
    embed.add_field(name=f"{emojis_bloons["ROUNDS"]} Rounds", value=f"{data["startRound"]}-{data["endRound"]}")
    embed.add_field(name=f"{emojis_bloons["MAX_MONKEYS"]} Max Monkeys", value=f"{data["maxTowers"]}")
    embed.add_field(name=f"{emojis_bloons["MAX_PARAGONS"]} Max Paragons", value=data["maxParagons"])
    embed.add_field(name=f"{emojis_bloons["MAP"]} Map", value=data["map"])
    embed.add_field(
        name=f"{emojis_bloons["ABILITY_COOLDOWN_INCREASE"] if data["abilityCooldownReductionMultiplier"] >= 1 else emojis_bloons["ABILITY_COOLDOWN_DECREASE"]} Ability Cooldown",
        value=f"{data["abilityCooldownReductionMultiplier"] * 100:.2f}%",
    )
    embed.add_field(
        name=f"{emojis_bloons["REMOVABLE_COST_INCREASE"] if data["removeableCostMultiplier"] >= 1 else emojis_bloons["REMOVABLE_COST_DECREASE"]} Removable Cost",
        value=f"{data["removeableCostMultiplier"] * 100:.2f}%",
    )
    bm = data["_bloonModifiers"]
    embed.add_field(
        name=f"{emojis_bloons["REGROW_RATE_INCREASE"] if bm["regrowRateMultiplier"] >= 1 else emojis_bloons["REGROW_RATE_DECREASE"]} Regrow Rate",
        value=f"{data["removeableCostMultiplier"] * 100:.2f}%",
    )
    embed.add_field(
        name=f"{emojis_bloons["BLOON_SPEED_INCREASE"] if bm["speedMultiplier"] >= 1 else emojis_bloons["BLOON_SPEED_DECREASE"]} Bloon Speed",
        value=f"{bm["speedMultiplier"] * 100:.2f}%",
    )
    embed.add_field(
        name=f"{emojis_bloons["MOAB_SPEED_INCREASE"] if bm["moabSpeedMultiplier"] >= 1 else emojis_bloons["MOAB_SPEED_DECREASE"]} MOAB Speed",
        value=f"{bm["moabSpeedMultiplier"] * 100:.2f}%",
    )
    embed.add_field(
        name=f"{emojis_bloons["BOSS_SPEED_INCREASE"] if bm["bossSpeedMultiplier"] >= 1 else emojis_bloons["BOSS_SPEED_DECREASE"]} Boss Speed",
        value=f"{bm["bossSpeedMultiplier"] * 100:.2f}%",
    )
    hm = bm["healthMultipliers"]
    embed.add_field(
        name=f"{emojis_bloons["CERAMIC_HP_INCREASE"] if hm["bloons"] >= 1 else emojis_bloons["CERAMIC_HP_DECREASE"]} Ceramic HP",
        value=f"{hm["bloons"] * 100:.2f}%",
    )
    embed.add_field(
        name=f"{emojis_bloons["MOAB_HP_INCREASE"] if hm["moabs"] >= 1 else emojis_bloons["MOAB_HP_DECREASE"]} MOAB HP",
        value=f"{hm["moabs"] * 100:.2f}%",
    )
    embed.add_field(
        name=f"{emojis_bloons["BOSS_HP_INCREASE"] if hm["boss"] >= 1 else emojis_bloons["BOSS_HP_DECREASE"]} Boss HP",
        value=f"{hm["boss"] * 100:.2f}%",
    )
    embed.set_thumbnail(url=thumbnail)
    return embed


class ElementalMasteryModal(Modal):
    level = TextInput(
        label="Level",
        placeholder="What is the character's level?",
        default="90",
        max_length=8,
    )
    elemental_mastery = TextInput(
        label="Elemental Mastery",
        placeholder="What is the character's Elemental Mastery?",
        max_length=8,
    )
    reaction_bonus = TextInput(
        label="Reaction Bonus",
        placeholder="Any additional damage bonus for reactions.",
        default="0",
        max_length=8,
    )

    def __init__(self, view):
        super().__init__(title="Elemental Mastery Calculator")
        self.view = view

    def is_finished(self, *_args, **_kwargs):
        return False

    async def on_submit(self, interaction: discord.Interaction, /):
        level = self.level.default = self.level.value
        elemental_mastery = self.elemental_mastery.default = self.elemental_mastery.value
        reaction_bonus = self.reaction_bonus.default = self.reaction_bonus.value
        if not level.isdigit():
            return await interaction.response.send_message(":x: Invalid **Level**. Please try again.", ehemeral=True)
        level = int(level)
        if level < 1 or level > 100:
            return await interaction.response.send_message(":x: Invalid **Level**. Please try again.", ehemeral=True)
        if not elemental_mastery.isdigit():
            return await interaction.response.send_message(":x: Invalid **Elemental Mastery**. Please try again.", ephemeral=True)
        if not reaction_bonus.isdigit():
            return await interaction.response.send_message(":x: Invalid **Reaction Bonus**. Please try again.", ephemeral=True)
        elemental_mastery = int(elemental_mastery)
        reaction_bonus = int(reaction_bonus)
        x = 2.78 * elemental_mastery / (elemental_mastery + 1_400) * 100 + reaction_bonus
        y = 16 * elemental_mastery / (elemental_mastery + 2000) * 100 + reaction_bonus
        z = 5 * elemental_mastery / (elemental_mastery + 1_200) * 100 + reaction_bonus
        w = 4.44 * elemental_mastery / (elemental_mastery + 1_400) * 100 + reaction_bonus
        rb_embed = discord.Embed(title="Elemental Reaction Bonus", color=0x4cc2f0)
        rb_embed.add_field(name="Level", value=level)
        rb_embed.add_field(name="Elemental Mastery", value=elemental_mastery)
        rb_embed.add_field(name="Reaction Bonus", value=f"{reaction_bonus}%")
        rb_embed.add_field(name="Amplifying Bonus", value=f"{x:.2f}%")
        rb_embed.add_field(name="Transformative Bonus", value=f"{y:.2f}%")
        rb_embed.add_field(name="Additive Bonus", value=f"{z:.2f}%")
        rb_embed.add_field(name="Crystallize Bonus", value=f"{w:.2f}%")
        rdy = levels[level] * (y + 100) / 100
        rdz = levels[level] * (z + 100) / 100
        rdw = shields[level] * (w + 100) / 100
        rd_embed = discord.Embed(title="Elemental Reaction Damage", color=0xaf8ec1)
        rd_embed.add_field(name="Burning", value=f"{.25 * rdy:.2f}")
        rd_embed.add_field(name="Swirl", value=f"{.6 * rdy:.2f}")
        rd_embed.add_field(name="Superconduct", value=f"{1.5 * rdy:.2f}")
        rd_embed.add_field(name="Electro-Charged, Bloom", value=f"{2 * rdy:.2f}")
        rd_embed.add_field(name="Overloaded", value=f"{2.75 * rdy:.2f}")
        rd_embed.add_field(name="Burgeon, Hyperbloom, Shatter", value=f"{3 * rdy:.2f}")
        rd_embed.add_field(name="Aggravate", value=f"{rdz * 1.15:.2f}")
        rd_embed.add_field(name="Spread", value=f"{rdz * 1.25:.2f}")
        rd_embed.add_field(name="Crystallize", value=f"{rdw:.2f}")
        await interaction.response.edit_message(content="", embeds=[rb_embed, rd_embed])


class ElementalMasteryView(BaseView):
    def __init__(self, ctx: commands.Context):
        super().__init__(ctx)
        self.modal = ElementalMasteryModal(self)

    @button(style=discord.ButtonStyle.secondary, label="Calculate", emoji="\N{CYCLONE}")
    async def calculate(self, interaction: discord.Interaction, _):
        await interaction.response.send_modal(self.modal)


class RPSView(BaseView):
    def __init__(self, player1, player2, player2_choice=None):
        super().__init__(ctx=None)
        self.player1 = player1
        self.player2 = player2
        self.player1_choice = None
        self.player2_choice = player2_choice

    async def pick_choice(self, interaction: discord.Interaction, choice):
        if interaction.user == self.player1:
            self.player1_choice = choice
        else:
            self.player2_choice = choice
        await interaction.response.send_message(f"You picked {rps_pretty[choice]}.", ephemeral=True)
        if self.player1_choice is None or self.player2_choice is None:
            return
        embed = discord.Embed(color=int(interaction.client.config["bot"]["color"], 16))
        a = format_username(self.player1)
        b = format_username(self.player2)
        embed.add_field(name=a, value=rps_pretty[self.player1_choice])
        embed.add_field(name=b, value=rps_pretty[self.player2_choice])
        if self.player1_choice == self.player2_choice:
            embed.title = ":handshake: The game is a draw."
        elif (self.player1_choice - self.player2_choice) % 3 == 1:
            embed.title = f"\N{CROSSED SWORDS} {a} defeated {b}!"
        else:
            embed.title = f"\N{SHIELD} {b} defeated {a}!"
        self.done = True
        await interaction.message.edit(content="", embed=embed, view=None)

    @button(style=discord.ButtonStyle.secondary, label="Rock", emoji="\N{MOYAI}")
    async def rock(self, interaction: discord.Interaction, _btn):
        await self.pick_choice(interaction, 0)

    @button(style=discord.ButtonStyle.secondary, label="Paper", emoji="\N{NEWSPAPER}")
    async def paper(self, interaction: discord.Interaction, _btn):
        await self.pick_choice(interaction, 1)

    @button(style=discord.ButtonStyle.secondary, label="Scissors", emoji="\N{BLACK SCISSORS}")
    async def scissors(self, interaction: discord.Interaction, _btn):
        await self.pick_choice(interaction, 2)

    async def interaction_check(self, interaction: discord.Interaction, /):
        return interaction.user.id in (self.player1.id, self.player2.id)


class Entertainment(commands.Cog):
    """A bunch of fun commands for the squad to use whenever you're bored."""
    help_emoji = "\N{VIDEO GAME}"
    help_color = 0xd4c44a

    def __init__(self, bot: commands.AutoShardedBot):
        super().__init__()
        self.bot = bot

    @commands.command()
    async def lenny(self, ctx: commands.Context):
        """( ͡° ͜ʖ ͡°)"""
        await ctx.reply("( ͡° ͜ʖ ͡°)")

    @commands.command()
    async def em(self, ctx: commands.Context):
        """Calculate Elemental Mastery"""
        view = ElementalMasteryView(ctx)
        message = await ctx.reply("Click **\N{CYCLONE} Calculate** to get started.", view=view)
        view.message = message

    async def _get_bloons_resource(self, url: str, redis_name: str):
        resource = self.bot.redis.get(redis_name)
        if resource:
            return json.loads(resource)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                body = await response.json()
                resource = body.get("body") if body.get("success") else None
                self.bot.redis.set(redis_name, json.dumps(resource, separators=(",", ":")))
                self.bot.redis.expire(redis_name, 43200)
                return resource

    @commands.group(invoke_without_command=True)
    @commands.cooldown(1, 15.0, commands.BucketType.user)
    async def bloons(self, ctx: commands.Context):
        """Really useful Bloons TD 6 commands"""
        await ctx.reply("- **Official website**: <https://btd6.com/>\n- **Steam**: <https://store.steampowered.com/app/960090/Bloons_TD_6/>\n- **Wiki**: <https://www.bloonswiki.com/>\n-# I am not affiliated with Ninja Kiwi. I just like their games.")

    @bloons.command()
    async def boss(self, ctx: commands.Context):
        """Get boss information"""
        message = await ctx.reply(":hourglass: Fetching resources...")
        bosses = await self._get_bloons_resource("https://data.ninjakiwi.com/btd6/bosses", "bloons:bosses")
        embeds = []
        for boss in bosses:
            standard = await self._get_bloons_resource(boss["metadataStandard"], f"bloons:bosses:{boss["id"]}:standard")
            if standard:
                embeds.append(create_bloons_document(standard, color=0xf4c600, thumbnail=boss_thumbnails[boss["bossType"]]))
            elite = await self._get_bloons_resource(boss["metadataElite"], f"bloons:bosses:{boss["id"]}:elite")
            if elite:
                embeds.append(create_bloons_document(elite, color=0x7b00f4, thumbnail=boss_thumbnails[f"{boss["bossType"]}-elite"]))
        await EmbedPaginator(ctx, embeds, message=message).start()

    @bloons.command(aliases=["daily", "advanced", "coop"])
    async def challenge(self, ctx: commands.Context):
        """Get daily challenge information"""
        message = await ctx.reply(":hourglass: Fetching resources...")
        challenges = await self._get_bloons_resource("https://data.ninjakiwi.com/btd6/challenges/filter/daily", "bloons:challenges:daily")
        embeds = []
        for challenge in challenges:
            document = await self._get_bloons_resource(challenge["metadata"], f"bloons:challenges:daily:{challenge["id"]}")
            if document:
                # TODO: bloonswiki.com doesn't have DailyChallengeBtn.png
                embed = create_bloons_document(
                    document,
                    color=challenge_color(challenge["id"]),
                    thumbnail="https://static.wikia.nocookie.net/b__/images/b/bf/DailyChallengeBtn.png/revision/latest/scale-to-width-down/100?cb=20200601042405&path-prefix=bloons",
                )
                embeds.append(embed)
        await EmbedPaginator(ctx, embeds, message=message).start()

    @bloons.command()
    async def race(self, ctx: commands.Context):
        """Get race information"""
        message = await ctx.reply(":hourglass: Fetching resources...")
        races = await self._get_bloons_resource("https://data.ninjakiwi.com/btd6/races", "bloons:races")
        embeds = []
        for race in races:
            document = await self._get_bloons_resource(race["metadata"], f"bloons:races:{race["id"]}")
            if document:
                embeds.append(create_bloons_document(document, color=0xffc300, thumbnail="https://www.bloonswiki.com/images/2/24/BTD6_EventRaceIcon.png"))
        await EmbedPaginator(ctx, embeds, message=message).start()

    @commands.command(aliases=["die", "dice"])
    async def roll(self, ctx: commands.Context, syntax):
        """Roll dice using AdX format"""
        matches = _roll_r.search(syntax)
        if matches is None:
            return await ctx.reply(":x: Invalid dice notation. Please try again.")
        groups = matches.groups()
        a = int(groups[0] or 1)
        x = int(groups[1] or 6)
        b = int(groups[2] or 0)
        results = ""
        total = b
        for _ in range(a):
            roll = randint(1, x)
            results += f" + {f"**{roll}**" if roll == x else roll}"
            total += roll
        embed = discord.Embed(
            title=f"You rolled {total} \N{GAME DIE}",
            description=results[3:],
            color=int(ctx.bot.config["bot"]["color"], 16),
        )
        embed.add_field(name="Dice", value=a)
        embed.add_field(name="Faces", value=x)
        embed.add_field(name="Addend", value=b)
        embed.set_footer(text=f"{a}d{x}{b if b < 0 else f"+{b}"}")
        await ctx.reply(embed=embed)

    @commands.command()
    async def rps(self, ctx: commands.Context, member: discord.Member = None):
        """Play Rock Paper Scissors"""
        if member is None:
            member = ctx.guild.me
        elif ctx.author == member:
            return
        view = RPSView(ctx.author, member, randint(0, 2) if member.bot else None)
        message = await ctx.reply(content=f"{ctx.author.mention} challenged {member.mention} to Rock Paper Scissors!", view=view)
        view.message = message

    async def _urban(self, term: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.urbandictionary.com/v0/define?term={quote(term)}") as response:
                data = await response.json()
                return data["list"]

    @commands.command(aliases=["define", "definition", "dictionary", "term"])
    async def urban(self, ctx: commands.Context, *, term):
        """Define a word"""
        url = "https://www.urbandictionary.com/define.php?term="
        words = await self._urban(term)
        embeds = []
        for word in words:
            embed = discord.Embed(
                title=word["word"],
                url=word["permalink"],
                description=_urban_r.sub(lambda m: f"[{m.group(1)}]({url}{quote(m.group(1))})", word["definition"]),
                timestamp=datetime.fromisoformat(word["written_on"]),
            )
            embed.add_field(name="\N{THUMBS UP SIGN}", value=word["thumbs_up"])
            embed.add_field(name="\N{THUMBS DOWN SIGN}", value=word["thumbs_down"])
            embed.set_footer(text=f"By {word["author"]}")
            embeds.append(embed)
        if len(embeds) < 0:
            return await ctx.reply(":x: No definitions found.")
        await EmbedPaginator(ctx, embeds).start()


async def setup(bot):
    await bot.add_cog(Entertainment(bot))
