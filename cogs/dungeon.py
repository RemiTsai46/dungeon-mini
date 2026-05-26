import discord
from discord.ext import commands
from utils.db import app, db, get_player_data
from game.soul_moves import SOUL_REGISTRY
from game.enemy_moves import spawn_enemy_by_level # Assuming your previous level setup
from game.entity import CombatEntity

class ActiveMatch:
    def __init__(self, player_id: int, equipped_ids: list, room_level: int):
        self.player_id = player_id
        
        # Initialize empty 4-plot grids
        self.team = [None, None, None, None]
        self.enemies = [None, None, None, None]
        
        # --- PHASE 1: Populate Our Side ---
        # equipped_ids looks like: [301, None, 302, None]
        for slot_idx, soul_id in enumerate(equipped_ids):
            if soul_id is not None and soul_id in SOUL_REGISTRY:
                blueprint = SOUL_REGISTRY[soul_id]
                # Put a fresh CombatEntity into the specific plot position
                self.team[slot_idx] = CombatEntity(
                    slot_id=slot_idx, 
                    entity_id=soul_id, 
                    blueprint=blueprint
                )
                
        # --- PHASE 2: Populate Enemy Side ---
        # Let's spawn 2 enemies for this room level as an example
        # In a real room setup, you can customize which plots get filled
        for slot_idx in [1, 2]: # Spawning enemies specifically in Plot 2 and Plot 3
            self.enemies[slot_idx] = spawn_enemy_by_level(level=room_level, slot_index=slot_idx)

        # --- PHASE 3: Turn State Tracking ---
        self.current_side = 0 # player 0 enemy 1
        self.current_plot = 0 
        
        # Adjust turn pointer if our very first plot happens to be empty
        if self.team[0] is None:
            self.find_next_valid_plot()

    def find_next_valid_plot(self):
        """Helper to advance plot pointer if a slot is completely empty."""
        # We will loop this later, but for setup, it guarantees 
        # self.current_plot points to a living entity when a match begins.
        pass

class GameEngine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Memory Storage: Maps (guild_id, user_id) -> ActiveMatch instance
        self.active_matches = {}

    @commands.hybrid_command(name="dungeon", description="Start a dungeon match.")
    async def start_dungeon(self, ctx: commands.Context):
        user_id = ctx.author.id
        guild_id = ctx.guild.id
        session_key = (guild_id, user_id)
        
        pdata = get_player_data(guild_id, user_id)
        
        # 1. Conflict Check using our State System
        if pdata.current_state != "idle":
            await ctx.send(f"❌ You are already busy doing a `{pdata.current_state}`!", ephemeral=True)
            return

        # 2. Lock the player's state in the Database
        with app.app_context():
            # Re-fetch within context to update safely
            player = User.query.filter_by(guild_id=guild_id, user_id=user_id).first()
            player.current_state = "dungeon"
            db.session.commit()

        # 3. Create the match status in RAM
        # Let's spawn a Goblin with 50 HP
        new_match = ActiveMatch(player_id=user_id, enemy_name="Goblin", enemy_hp=50)
        self.active_matches[session_key] = new_match

        # 4. Send Game UI
        embed = discord.Embed(title="⚔️ Dungeon Encounter", color=discord.Color.red())
        embed.add_field(name="Enemy", value=f"**{new_match.enemy_name}**")
        embed.add_field(name="HP", value=f"❤️ {new_match.current_hp}/{new_match.max_hp}")
        embed.set_footer(text=f"Round {new_match.round}")
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="attack", description="Execute an action for your active Sword Soul.")
    async def attack(self, ctx: commands.Context, skill_slot: int, target_slot: int):
        user_id = ctx.author.id
        session_key = (ctx.guild.id, user_id)

        if session_key not in self.active_matches:
            await ctx.send("You aren't in a match!", ephemeral=True)
            return

        match = self.active_matches[session_key]
        attacker = match.team[match.current_turn_index]

        # 1. Validation: Is the selected target slot valid?
        if target_slot < 1 or target_slot > 4 or match.enemies[target_slot - 1] is None:
            await ctx.send("❌ Invalid target slot! Choose an occupied enemy slot (1-4).", ephemeral=True)
            return
            
        target_enemy = match.enemies[target_slot - 1]

        # 2. Process Damage Calculation
        damage = 25 # Calculate based on skill_slot later
        target_enemy.current_hp -= damage
        
        result_msg = f"⚔️ **{attacker.name}** (Slot {match.current_turn_index + 1}) used Skill {skill_slot} on **{target_enemy.name}** (Slot {target_slot}) for {damage} DMG!\n"

        # 3. Check Enemy Death
        if target_enemy.current_hp <= 0:
            result_msg += f"💀 **{target_enemy.name}** was defeated!\n"
            match.enemies[target_slot - 1] = None # Clear enemy slot

        # 4. Check Global Win Condition
        if all(e is None for e in match.enemies):
            await ctx.send(result_msg + "🎉 **Victory! All enemies cleared!**")
            # Handle DB reward saving and cleanup here...
            del self.active_matches[session_key]
            return

        # 5. Move to Next Turn Pointer
        match.advance_turn()
        next_attacker = match.team[match.current_turn_index]

        # 6. Build and Send UI showing updated HP tables
        embed = discord.Embed(title=f"Round {match.round}", description=result_msg, color=discord.Color.blue())
        # Add visual list of enemies and players here...
        embed.set_footer(text=f"Next up: Slot {match.current_turn_index + 1} ({next_attacker.name})")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(GameEngine(bot))