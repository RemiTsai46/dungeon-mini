import discord
from discord.ext import commands
from utils.db import get_or_create_user, update_character_level

class GeneralCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="profile", description="Check your game profile")
    async def profile(self, ctx: commands.Context):
        # Fetch or create the profile instantly
        player = get_or_create_user(ctx.guild.id, ctx.author.id)
        
        embed = discord.Embed(title=f"{ctx.author.display_name}'s Profile")
        embed.add_field(name="Equipped IDs", value=str(player.equipped_characters))
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="levelup", description="Level up starter character")
    async def levelup(self, ctx: commands.Context):
        # Update character 101 directly
        success = update_character_level(ctx.guild.id, ctx.author.id, "101", 2)
        
        if success:
            await ctx.send("Your starter character is now Level 2!")
        else:
            await ctx.send("Profile not found. Use /profile first.")

async def setup(bot):
    await bot.add_cog(GeneralCommands(bot))