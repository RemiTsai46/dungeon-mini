import discord
from discord.ext import commands
from utils import db

ICON_PATH = "images/dungeon_mini_icon.png"

# class Buttons(discord.ui.View):
#     @discord.ui.button(label="<<", row=0, style=discord.ButtonStyle.primary)
#     async def prv_pg(self, interaction, button):
#         await interaction.response.send_message("start!", ephemeral = True)

#     @discord.ui.button(label=">>", row=0, style=discord.ButtonStyle.primary)
#     async def nxt_pg(self, interaction, button):
#         await interaction.response.send_message("start!", ephemeral = True)

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="stats", description="View your stats.")
    async def character_view(self, ctx: commands.Context):
        user = ctx.author
        guild_id = ctx.guild.id
        user_id = user.id
        game_icon = discord.File(ICON_PATH, filename="icon.png")

        await ctx.defer(ephemeral=False)

        user_data = db.get_player_data(guild_id,user_id)

        embed = discord.Embed(
            title=f"{user.display_name} 's Stats",
            color=discord.Color.blue()
        )
        embed.set_author(name=user.name, icon_url=user.display_avatar.url)
        embed.set_thumbnail(url="attachment://icon.png")
        embed.add_field(name="Current Level", value=f"Room **{user_data.curr_room}**, Level **{user_data.curr_level}**")
        embed.add_field(name="Current Status", value=user_data.curr_state)
        await ctx.send(file=game_icon, embed=embed)

async def setup(bot):
    await bot.add_cog(Status(bot))