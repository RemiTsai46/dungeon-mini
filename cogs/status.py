import discord
from discord.ext import commands
from discord import app_commands

class Buttons(discord.ui.View):
    @discord.ui.button(label="<<", row=0, style=discord.ButtonStyle.primary)
    async def prv_pg(self, interaction, button):
        await interaction.response.send_message("start!", ephemeral = True)

    @discord.ui.button(label=">>", row=0, style=discord.ButtonStyle.primary)
    async def nxt_pg(self, interaction, button):
        await interaction.response.send_message("start!", ephemeral = True)

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="status", description="View your status.")
    async def character_view(self, ctx: commands.Context):
        user = ctx.author

        embed = discord.Embed(
            title="Status",
            description="View your status"
        )

        msg = await ctx.send(embed=embed, view=Buttons()) # TBA store user current embed message id

async def setup(bot):
    await bot.add_cog(Status(bot))