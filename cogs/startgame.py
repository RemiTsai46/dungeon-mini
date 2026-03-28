import discord
from discord.ext import commands
from discord import app_commands

ICON_PATH = "images/dungeon_mini_icon.png"

class Buttons(discord.ui.View):
    @discord.ui.button(label="start!", style=discord.ButtonStyle.primary)
    async def start_button(self, interaction, button):
        await interaction.response.send_message("start!", ephemeral = True)

class GeneralCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="start-game", description="Start playing Dungeon Mini!")
    async def start_game(self, ctx: commands.Context):
        game_icon = discord.File(ICON_PATH, filename="icon.png")

        embed = discord.Embed()
        embed.set_image(url="attachment://icon.png")
        # await interaction.response.send_message(file=game_icon, embed=embed, view=Buttons())
        msg = await ctx.send(file=game_icon, embed=embed, view=Buttons()) # TBA store user current embed message id

    @commands.hybrid_command(name="nuke",description=r"Delete {count} messages")
    @commands.has_permissions(manage_messages=True)
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.describe(count="message count")
    async def nuke(self, ctx: commands.Context, count: int = 0):
        if count < 1:
            await ctx.send("Amount of messages must be >0",ephemeral=True)
            return
        
        await ctx.defer(ephemeral=True)
        deleted = await ctx.channel.purge(limit=count)
        await ctx.send(f"Deleted {len(deleted)} message(s)",ephemeral=True)


async def setup(bot):
    await bot.add_cog(GeneralCommands(bot))