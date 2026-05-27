import discord
from discord.ext import commands
from utils import db 
from game.match import ActiveMatch

class Dungeon(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="dungeon", description="Start a dungeon run.")
    async def dungeon(self, ctx: commands.Context):
        # 1. Defer the response immediately to prevent Discord's 3-second timeout
        await ctx.defer(ephemeral=False)
        
        guild_id = ctx.guild.id
        user_id = ctx.author.id

        if not db.is_player_idle(guild_id, user_id):
            await ctx.send(
                "❌ **You cannot do that right now!** You are already busy or in a match.", 
                ephemeral=True
            )
            return
        
        # 2. Update player state in the DB to prevent multi-queueing exploits
        # (Assumes your db file has a function to handle status updating)
        db.set_player_status(guild_id, user_id, "dungeon")
        
        # 3. Create and send the initial loading layout embed
        embed = discord.Embed(
            title="⚔️ Entering the Dungeon...", 
            description="Preparing the battlefield and loading your Soul stats...",
            color=0x442200
        )

        match_msg = await ctx.send(embed=embed)
        interaction = ctx.interaction
        
        # 4. Instantiate the game match engine
        # We pass the interaction and the message objects so the engine can edit it later
        match = ActiveMatch(
            guild_id=guild_id,
            player_id=user_id,
            message=match_msg,
        )
        
        # 5. Kick off the asynchronous core game loop inside game/classes.py
        await match.start_loop()

async def setup(bot):
    await bot.add_cog(Dungeon(bot))