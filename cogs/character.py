import discord
from discord.ext import commands
from discord import app_commands

class Buttons(discord.ui.View):
    @discord.ui.button(label="1", row="0", style=discord.ButtonStyle.primary)
    async def start_button(self, interaction, button):
        await interaction.response.send_message("start!", ephemeral = True)

class GeneralCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="Character", description="Open the character interface")
    async def start_game(self, ctx: commands.Context):
        embed = discord.Embed(title="Character")
        # await interaction.response.send_message(file=game_icon, embed=embed, view=Buttons())
        msg = await ctx.send(embed=embed, view=Buttons()) # TBA store user current embed message id

async def setup(bot):
    await bot.add_cog(GeneralCommands(bot))