import discord
from discord.ext import commands
from discord import app_commands

class Buttons(discord.ui.View):
    @discord.ui.button(label="1", row=0, style=discord.ButtonStyle.primary)
    async def slot_1(self, interaction, button):
        await interaction.response.send_message("start!", ephemeral = True)

    @discord.ui.button(label="2", row=0, style=discord.ButtonStyle.primary)
    async def slot_2(self, interaction, button):
        await interaction.response.send_message("start!", ephemeral = True)

    @discord.ui.button(label="3", row=0, style=discord.ButtonStyle.primary)
    async def slot_3(self, interaction, button):
        await interaction.response.send_message("start!", ephemeral = True)

    @discord.ui.button(label="4", row=0, style=discord.ButtonStyle.primary)
    async def slot_4(self, interaction, button):
        await interaction.response.send_message("start!", ephemeral = True)

    @discord.ui.button(label="5", row=0, style=discord.ButtonStyle.primary)
    async def slot_5(self, interaction, button):
        await interaction.response.send_message("start!", ephemeral = True)

    @discord.ui.button(label="6", row=1, style=discord.ButtonStyle.primary)
    async def slot_6(self, interaction, button):
        await interaction.response.send_message("start!", ephemeral = True)

    @discord.ui.button(label="7", row=1, style=discord.ButtonStyle.primary)
    async def slot_7(self, interaction, button):
        await interaction.response.send_message("start!", ephemeral = True)

    @discord.ui.button(label="8", row=1, style=discord.ButtonStyle.primary)
    async def slot_8(self, interaction, button):
        await interaction.response.send_message("start!", ephemeral = True)

    @discord.ui.button(label="9", row=1, style=discord.ButtonStyle.primary)
    async def slot_9(self, interaction, button):
        await interaction.response.send_message("start!", ephemeral = True)

    @discord.ui.button(label="10", row=1, style=discord.ButtonStyle.primary)
    async def slot_10(self, interaction, button):
        await interaction.response.send_message("start!", ephemeral = True)

class Character(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="character", description="Open the character interface")
    async def character_view(self, ctx: commands.Context):
        user = ctx.author

        embed = discord.Embed(
            title="Character",
            description="View your characters"
        )
        embed.set_author(name=user.name, icon_url=user.display_avatar.url)
        embed.add_field(name=":emoji: name", value="des", inline=True)
        embed.add_field(name="huh", value="oh", inline=True)
        embed.add_field(name="3", value="th", inline=True)
        embed.add_field(name="4", value="ffr", inline=True)

        # await interaction.response.send_message(file=game_icon, embed=embed, view=Buttons())
        msg = await ctx.send(embed=embed, view=Buttons()) # TBA store user current embed message id

async def setup(bot):
    await bot.add_cog(Character(bot))