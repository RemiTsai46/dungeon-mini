import discord
from discord.ext import commands
from discord import app_commands

class Buttons(discord.ui.View):
    @discord.ui.button(label="m1", row=0, style=discord.ButtonStyle.primary)
    async def m1(self, interaction, button):
        await interaction.response.send_message("start!", ephemeral = True)

    @discord.ui.button(label="skill", row=0, style=discord.ButtonStyle.primary)
    async def skill(self, interaction, button):
        await interaction.response.send_message("start!", ephemeral = True)

    @discord.ui.button(label="ult", row=0, style=discord.ButtonStyle.primary)
    async def ult(self, interaction, button):
        await interaction.response.send_message("start!", ephemeral = True)

class Dungeon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="dungeon", description="Challenge the dungeon!")
    async def character_view(self, ctx: commands.Context):
        user = ctx.author

        embed = discord.Embed(
            title="Dungeon",
            description="Challenge the dungeon!"
        )

        msg = await ctx.send(embed=embed, view=Buttons()) # TBA store user current embed message id

async def setup(bot):
    await bot.add_cog(Dungeon(bot))