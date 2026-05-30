import discord
import traceback
from discord.ext import commands
from utils import db 
from game.match import ActiveMatch

class Dungeon(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="dungeon", description="Start a dungeon run.")
    async def dungeon(self, ctx: commands.Context):
        try:
            guild_id = ctx.guild.id
            user_id = ctx.author.id

            if not db.is_player_idle(guild_id, user_id):
                await ctx.send(
                    "❌ **You cannot do that right now!** You are already busy or in a match.", 
                    ephemeral=True
                )
                return
            
            await ctx.defer(ephemeral=False)
            
            print("hello1")
            # 2. Update player state in the DB to prevent multi-queueing exploits
            # (Assumes your db file has a function to handle status updating)
            db.set_player_state(guild_id, user_id, "dungeon")
            print("hello2")
        
        
            # 3. Create initial loading layout embed
            embed = discord.Embed(
                title="⚔️ Intermission ⚔️", 
                description="Setting up the level...",
                color=0x442200
            )

            # FIX: Use ctx.interaction.followup.send because the command was deferred
            match_msg = await ctx.interaction.followup.send(embed=embed)
            
            # 4. Instantiate the game match engine
            match = ActiveMatch(
                guild_id=guild_id,
                player_id=user_id,
                message=match_msg, # Engine gets the actual interactive message object
            )
            
            # 5. Kick off the core game loop
            await match.start_match()

        except Exception as e:
            # If the engine crashes, log it and tell the user so it doesn't freeze silently
            print(f"[CRITICAL ERROR DURING MATCH]: {e}")
            traceback.print_exc()
            
            try:
                await ctx.interaction.followup.send(
                    "⚠️ **An internal match error occurred.** Your dungeon run has been terminated.",
                    ephemeral=True
                )
            except Exception:
                pass
        
        finally:
            # FIX: No matter what happens (clean exit or hard crash), unlock the player account!
            print(f"[CLEANUP] Releasing lock for user {user_id}")
            db.set_player_state(guild_id, user_id, "idle")

async def setup(bot):
    await bot.add_cog(Dungeon(bot))