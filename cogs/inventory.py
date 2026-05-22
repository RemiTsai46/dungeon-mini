import discord
from discord.ext import commands
from discord import app_commands
from utils.db import get_player_data

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

    @discord.ui.button(label="4", row=1, style=discord.ButtonStyle.primary)
    async def slot_4(self, interaction, button):
        await interaction.response.send_message("start!", ephemeral = True)

    @discord.ui.button(label="5", row=1, style=discord.ButtonStyle.primary)
    async def slot_5(self, interaction, button):
        await interaction.response.send_message("start!", ephemeral = True)

    @discord.ui.button(label="6", row=1, style=discord.ButtonStyle.primary)
    async def slot_6(self, interaction, button):
        await interaction.response.send_message("start!", ephemeral = True)

    @discord.ui.button(label="<<", row=2, style=discord.ButtonStyle.primary)
    async def prv_pg(self, interaction, button):
        await interaction.response.send_message("start!", ephemeral = True)

    @discord.ui.button(label=">>", row=2, style=discord.ButtonStyle.primary)
    async def nxt_pg(self, interaction, button):
        await interaction.response.send_message("start!", ephemeral = True)

class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="inventory", description="View your inventory.")
    async def character_view(self, ctx: commands.Context):
        user = ctx.author
        user_id = user.id
        guild_id = ctx.guild.id
        pdata = get_player_data(guild_id,user_id)

        # Safety check: If the DB failed, stop here before printing!
        if pdata is None:
            print("[Cog Debug] pdata returned as None! Check the DB error above.")
            await ctx.send("An error occurred while loading your profile. Please check the bot logs.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Inventory",
            description="View your inventory",
            color=discord.Color.dark_gold()
        )
        embed.set_author(name=user.name, icon_url=user.display_avatar.url)
        embed.add_field(name="Elynn",value=f"<:elynn:1487375063996170283> {pdata.elynn}")
        embed.add_field(name="Azure Dust",value=f"<:azure_dust:1487824468662419506> {pdata.azure_dust}")
        embed.add_field(name="Azure Stone",value=f"<:azure_stone:1487825302196453516> {pdata.azure_stone}")

        await ctx.send(embed=embed, view=Buttons()) # TBA store user current embed message id

async def setup(bot):
    await bot.add_cog(Inventory(bot))