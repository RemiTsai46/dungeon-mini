import math
import asyncio
import discord
import time
from game.soul_moves import SOUL_REGISTRY
from game.enemy_moves import ENEMY_REGISTRY
from game.rooms import ROOM_REGISTRY
from game.effects import EFFECT_REGISTRY
from utils import db

PASSIVE_UNLOCK_LEVELS = {"p1": 40, "p2": 80, "p3": 120}
RARITY_PASSIVE_LIMITS = {"Rare": 1, "Epic": 2, "Legendary": 2, "Secret": 3}

class CombatEntity:
    def __init__(self, name:str, emoji:str, rarity:str, element:str, level:int, base_stats:dict, moves:dict, passives:dict):
        # Core Identity
        self.name = name
        self.emoji = emoji
        self.rarity = rarity
        self.element = element
        self.level = level
        self.magic_orbs = 0
        
        # Stat Calculations (Level 1 base stats scaling)
        self.max_hp = base_stats["hp"]
        self.current_hp = self.max_hp
        self.shield_hp = 0
        self.base_dmg = base_stats["dmg"]
        self.cc = base_stats["cc"] # crit chance
        self.dfs = base_stats["dfs"] # defense
        
        # Dynamic Custom Rule: +3% Critical Damage (cd) for every 20 levels
        intervals = self.level // 20
        self.cd = base_stats["cd"] + (intervals * 0.03)
        
        # Moves Kit and Passive Map
        self.moves = moves          # List of active move keys/IDs
        self.passives = passives    # Dict mapping e.g., {"p1": 101, "p2": None}
        
        # Active status monitoring (e.g., {"burn": {"duration": 2, "source_dmg": 15}})
        self.effects = {}
        self.action_buffs = {} # Temporary stat boosts wiped clean at round end
        self.recent_damage_taken = 0  

    def get_calculated_dmg(self) -> int:
        """Calculates dynamic attack power including active status modifiers."""
        multiplier = 1.0
        # Future hooks for checking damage-altering active statuses can be handled here
        return int(self.base_dmg * multiplier)


class ActiveMatch:
    def __init__(self, guild_id: int, player_id: int, message: discord.Message):
        self.guild_id = guild_id
        self.player_id = player_id
        self.message = message
        
        # Extract the native interaction directly from the message architecture if present
        self.interaction = message.interaction_metadata if hasattr(message, "interaction_metadata") else None
        
        self.combat_log = ""
        self.round_cntr = 1
        self.is_active = True
        
        self.allies = [None, None, None, None]  
        self.enemies = [None, None, None, None]
        self.curr_room = 1
        self.curr_level = 1
        
        self.last_activity_ts = time.time()

        self._teams_init()

    def _teams_init(self):
        try:
            """Fills the fixed 4-slot ally team from the database and spawns enemies."""
            user_data = db.get_player_data(self.guild_id, self.player_id)
            print(f"[DEBUG INIT] Fetching user data for Player: {self.player_id}")
            self.curr_room = getattr(user_data, "curr_room", 1)
            self.curr_level = getattr(user_data, "curr_level", 1)
            print(f"[DEBUG INIT] Loaded Room: {self.curr_room}, Level: {self.curr_level}")
            
            # === SOUL INIT ===

            # get soul data
            soul_slots = getattr(user_data, "equipped_souls", [None, None, None, None])
            owned_souls = getattr(user_data, "owned_souls", {})
            # fallback
            if all(slot is None for slot in soul_slots[:4]):
                soul_slots[0] = 301
                
            # put souls in place
            for index in range(4):
                soul_id = soul_slots[index]
                if soul_id is not None:
                    blueprint = SOUL_REGISTRY.get(soul_id)
                    if blueprint:
                        soul_data = owned_souls.get(soul_id) or owned_souls.get(str(soul_id))
                        if isinstance(soul_data, dict):
                            soul_level = soul_data.get("level", 1)
                        else:
                            soul_level = 1 # Fallback level if entry exists as non-dict structure
                        self.allies[index] = CombatEntity(
                            name=blueprint["name"],
                            emoji=blueprint["emoji"],
                            rarity=blueprint["rarity"],
                            element=blueprint["element"],
                            level=soul_level,
                            base_stats=blueprint["stats"],
                            moves=blueprint["moves"],
                            passives=blueprint["passives"]
                        )
                        print(f"[DEBUG INIT] Slot {index} Ally Loaded: {blueprint['name']}")
                    else:
                        print(f"[WARNING INIT] Soul ID {soul_id} missing from SOUL_REGISTRY!")
                        self.allies[index] = None
                else:
                    self.allies[index] = None


            # === ENEMY INIT ===

            self.room = ROOM_REGISTRY.get(user_data.curr_room, ROOM_REGISTRY[1])
            self.level = self.room.get(user_data.curr_level, {
                "type": "Normal", 
                "enemies": [None, {"id": 101, "level": 1}, {"id": 101, "level": 1}, None]
            })

            # Separate stage style descriptors from the character list structure
            level_type = self.level.get("type", "Normal")
            enemy_slots = self.level.get("enemies", [])
            
            # Fill missing slots to conform to standard 4-slot boundaries
            compiled_wave = enemy_slots.copy()
            while len(compiled_wave) < 4:
                compiled_wave.append(None)
            
            for index in range(4):
                enemy_data = compiled_wave[index]
                
                if isinstance(enemy_data, dict):
                    enemy_id = enemy_data.get("id")
                    enemy_level = enemy_data.get("level", 1)
                    
                    blueprint = ENEMY_REGISTRY.get(enemy_id)
                    if blueprint:
                        self.enemies[index] = CombatEntity(
                            name=blueprint['name'],
                            emoji=blueprint['emoji'],
                            rarity=blueprint['type'],
                            element=blueprint["element"],
                            level=enemy_level,
                            base_stats=blueprint["stats"],
                            moves=blueprint["moves"],
                            passives=blueprint["passives"]
                        )
                    else:
                        self.enemies[index] = None
                else:
                    self.enemies[index] = None

        except Exception as e:
            # Captures any breaking issues and dumps it straight to your terminal console
            print(f"[CRITICAL FAILURE IN TEAMS_INIT]: {e}")
            import traceback
            traceback.print_exc()

    def is_passive_unlocked(self, entity: CombatEntity, slot_key: str) -> bool:
        """Enforces slot validity metrics dictated by character rarity thresholds and levels."""
        allowed_count = RARITY_PASSIVE_LIMITS.get(entity.rarity, 0)
        slot_index_map = {"p1": 1, "p2": 2, "p3": 3}
        
        if slot_index_map[slot_key] > allowed_count:
            return False
            
        return entity.level >= PASSIVE_UNLOCK_LEVELS[slot_key]

    def execute_event_pipeline(self, entity: CombatEntity, event_trigger: str, context_payload: dict = None):
        """Unified lifecycle routing processing both character passives and status buffs."""
        if not entity or entity.current_hp <= 0:
            return

        # 1. Evaluate unlocked passives matching this trigger event context
        for slot, passive_id in entity.passives.items():
            if passive_id and self.is_passive_unlocked(entity, slot):
                effect_meta = EFFECT_REGISTRY.get(passive_id)
                if effect_meta and effect_meta["trigger"] == event_trigger:
                    effect_meta["func"](self, entity, context_payload)

        # 2. Evaluate active timed status adjustments matching this trigger event context
        active_buff_keys = list(entity.effects.keys())
        for status_key in active_buff_keys:
            effect_meta = EFFECT_REGISTRY.get(status_key)
            if effect_meta and effect_meta["trigger"] == event_trigger:
                # Send along the specific instance data (duration, power, etc.)
                status_instance_data = entity.effects[status_key]
                effect_meta["func"](self, entity, status_instance_data)

    async def start_match(self):
        """Initializes the match state and kicks off the very first turn phase."""
        self.combat_log="⚔️ The dungeon battle begins!"
        
        # Match Start: Every participant receives 3 starting magic orbs
        for entity in filter(None, self.allies + self.enemies):
            entity.magic_orbs = 3
            # self.execute_event_pipeline(entity, "ON_MATCH_START")
            
        # Initialize state pointers
        self.is_ally_phase = True
        self.active_plot_idx = 0  # 0-3
        
        await self.render_battlefield_view()
        await self.advance_turn_state()

    async def advance_turn_state(self):
        """Processes the state machine. Routes to player choices or automated enemy actions."""
        if not self.is_active:
            return

        # Check game-over conditions before starting any turn action
        if self._check_match_over():
            return

        # --- ALLY SIDE PHASE ---
        if self.is_ally_phase:
            while self.active_plot_idx < 4:
                attacker = self.allies[self.active_plot_idx]
                if attacker and attacker.current_hp > 0:
                    await self.render_battlefield_view(prompt_player_input=True)
                    return
                
                # If slot is empty or unit is dead, step forward linearly
                self.active_plot_idx += 1
            
            # If the loop completes, all 4 slots have been evaluated. Shift to Enemy Phase.
            self.is_ally_phase = False
            self.active_plot_idx = 0
            await self.advance_turn_state()
            return

        # --- ENEMY SIDE PHASE ---
        if not self.is_ally_phase:
            # Linear scan: look for the next valid living enemy slot without recurring
            while self.active_plot_idx < 4:
                enemy_attacker = self.enemies[self.active_plot_idx]
                if enemy_attacker and enemy_attacker.current_hp > 0:
                    await self._execute_enemy_automated_turn(enemy_attacker)
                    return
                
                # If slot is empty or enemy is dead, step forward linearly
                self.active_plot_idx += 1
            
            # If the loop completes, all 4 slots have been evaluated. Process Round-End Phase.
            await self._process_round_end()
            return

    def log_move_execution(self, attacker, move_key: str, move_data: dict):
        """Formats and writes the action header to the match combat logs."""
        move_name = move_data.get("name", "Unknown Move")
        target_type = move_data.get("target", "Single")
        
        # Determine descriptive headers based on move classification keys
        if move_key == "m1":
            prefix = "**[M1]**"
        elif move_key == "skl":
            prefix = "**[SKILL]**"
        elif move_key == "ult":
            prefix = "**[ULTIMATE CAST]**"
        else:
            prefix = "**[Action]**"

        target_desc = "the enemy ranks" if target_type == "Extended" else "a target"
        self.combat_log = f"{prefix} {attacker.emoji} **{attacker.name}** uses **{move_name}** against {target_desc}!"

    async def handle_player_move_selection(self, move_key: str, target_idx: int = None):
        """Callback invoked when a button interaction is sent by the player."""
        # Refresh the AFK activity timer
        self.last_activity_ts = time.time()
        attacker = self.allies[self.active_plot_idx]
        move_data = attacker.moves.get(move_key)
        
        if not move_data or attacker.magic_orbs < move_data.get("rqmo", 0):
            return 

        # Deduct resource costs
        attacker.magic_orbs -= move_data.get("rqmo", 0)

        # --- DETERMINISTIC TARGET SELECTION ---
        # If no target_idx was passed (e.g., they just pressed a button blindly),
        # Double check if their selected target slot is already dead
        if target_idx is None or self.enemies[target_idx] is None or self.enemies[target_idx].current_hp <= 0:
            for idx, enemy in enumerate(self.enemies):
                if enemy and enemy.current_hp > 0:
                    target_idx = idx
                    break

        self.log_move_execution(attacker, move_key, move_data)
        
        # Pass the verified target_idx down to your AoE/Single calculation scope
        targets = self._get_move_targets(self.enemies, target_idx, move_data.get("target", "Single"))

    async def render_battlefield_view(self, prompt_player_input: bool = False):
        """Compiles a beautifully aligned 4-row grid pairing allies and enemies side-by-side."""
        display_log = self.combat_log if self.combat_log else "*The iron gates raise...*"
        
        embed = discord.Embed(
            title=f"Dungeon - Room {self.curr_room} Level {self.curr_level} | Round {self.round_cntr}",
            description=display_log, 
            color=0x442200
        )

        if prompt_player_input and self.is_ally_phase:
            active_unit = self.allies[self.active_plot_idx]
            embed.set_footer(text=f"👉 It is {active_unit.name}'s turn (Plot {self.active_plot_idx + 1}) - Choose an action!")

        emojis = {
            "hp": "<:hp:1509871426314965103>",
            "orb": "<:magic_orb:1509871398246551572>",
            "effects": "🌟"
        }

        ally_total = ""
        enemy_total = ""

        for i in range(4):
            
            # --- ALLY SLOT FIELD GENERATION ---
            ally = self.allies[i]
            if ally:
                # Set arrow marker to the right of the name if this ally is active
                marker = "⬅️" if (prompt_player_input and self.is_ally_phase and i == self.active_plot_idx) else ""
                dmg_flash = f"-{ally.recent_damage_taken}" if ally.recent_damage_taken else ""
                shield_display = f"+ 🛡️{ally.shield_hp}" if ally.shield_hp > 0 else ""
                status_list = ", ".join(ally.effects.keys()) if ally.effects else ""
                
                ally_name = f"{ally.emoji} Lv.{ally.level} {ally.name}{marker}"
                
                if ally.current_hp <= 0:
                    ally_value = "💀 **ELIMINATED**"
                else:
                    # Layout Pattern: {hp-emoji} {hp} {recent-damage} \n {magic-orb-emoji} {mo} \n {effects-emoji} {effects}
                    ally_value = (
                        f"{emojis['hp']} {ally.current_hp}/{ally.max_hp} {shield_display}{dmg_flash}\n"
                        f"{emojis['orb']} {ally.magic_orbs}\n"
                        f"{emojis['effects']} {status_list}\n\n"
                    )
            else:
                ally_name = f"Soul {i+1}"
                ally_value = "Empty\n\n\n\n"

            ally_total += f"**{ally_name}**\n{ally_value}"

            # --- ENEMY SLOT FIELD GENERATION ---
            enemy = self.enemies[i]
            if enemy:
                # Set arrow marker to the right of the name if this enemy is active
                marker = "⬅️" if (not self.is_ally_phase and i == self.active_plot_idx and self.is_active) else ""
                dmg_flash = f"-{enemy.recent_damage_taken}" if enemy.recent_damage_taken else ""
                shield_display = f"+ 🛡️{enemy.shield_hp}" if enemy.shield_hp > 0 else ""
                status_list = ", ".join(enemy.effects.keys()) if enemy.effects else ""
                enemy_type = f"[{enemy.rarity}]" if enemy.rarity != "Normal" else ""
                
                # Layout Pattern: {character-emoji} [{type}] Lv.{character level} {character-name}{marker}
                enemy_name = f"{enemy.emoji} {enemy_type}Lv.{enemy.level} {enemy.name}{marker}"
                
                if enemy.current_hp <= 0:
                    enemy_value = "💀 **DEFEATED**"
                else:
                    # Layout Pattern: {hp-emoji} {hp} {recent-damage} \n {magic-orb-emoji} {mo} \n {effects-emoji} {effects}
                    enemy_value = (
                        f"{emojis['hp']} {enemy.current_hp}/{enemy.max_hp}{shield_display}{dmg_flash}\n"
                        f"{emojis['effects']} {status_list}\n\n\n"
                    )
            else:
                enemy_name = f"Enemy {i+1}"
                enemy_value = "Empty\n\n\n\n"

            enemy_total += f"**{enemy_name}**\n{enemy_value}"

        embed.add_field(name="Sword Souls", value=ally_total, inline=True)
        embed.add_field(name="Enemies", value=enemy_total, inline=True)
        
        # ===============
        # |   BUTTONS   |
        # ===============

        view = None
        if prompt_player_input and self.is_ally_phase and self.is_active:
            active_unit = self.allies[self.active_plot_idx]
            view = discord.ui.View(timeout=None)

            # TARGET SELECT
            select_options = []
            for idx, enemy in enumerate(self.enemies):
                if enemy and enemy.current_hp > 0:
                    select_options.append(discord.SelectOption(
                        label=f"Slot {idx + 1}: {enemy.name}",
                        description=f"HP: {enemy.current_hp}/{enemy.max_hp} | {enemy.rarity}",
                        value=str(idx)
                    ))

            if select_options:
                target_select = discord.ui.Select(
                    placeholder="🎯 Optional: Lock a primary target slot...",
                    options=select_options,
                    custom_id="target_select",
                    row=0
                )
                async def target_callback(interaction: discord.Interaction):
                    if interaction.user.id != self.player_id: return
                    self.interaction = interaction
                    await interaction.response.defer()
                    await self.render_battlefield_view(prompt_player_input=True)

                target_select.callback = target_callback
                view.add_item(target_select)
            
            # M1
            m1_info = active_unit.moves.get("m1", {})
            m1_name = m1_info.get("name", "")
            m1_btn = discord.ui.Button(
                label=f"M1 {m1_name}",
                style=discord.ButtonStyle.primary, 
                custom_id="btn_m1",
                row=1
            )
            async def m1_callback(interaction: discord.Interaction):
                if interaction.user.id != self.player_id: return
                # Look up the select menu component in the current view
                chosen_target = None
                for child in view.children:
                    if isinstance(child, discord.ui.Select) and child.custom_id == "target_select":
                        if child.values: 
                            chosen_target = int(child.values[0])
                
                # --- CRITICAL: EPHERMERAL TARGET CHECK ---
                if chosen_target is None:
                    await interaction.response.send_message(
                        f"❌ **Action Cancelled:** You must select a valid enemy target from the dropdown menu first!", 
                        ephemeral=True
                    )
                    return
                self.interaction = interaction 
                await interaction.response.defer()
                await self.handle_player_move_selection("m1",target_idx=chosen_target)
                
            m1_btn.callback = m1_callback
            view.add_item(m1_btn)
            
            # SKILL
            skill_info = active_unit.moves.get("skl", {})
            skill_name = skill_info.get("name", "Skill")
            skl_req_orbs = skill_info.get("rqmo", 3)
            has_skl_orbs = active_unit.magic_orbs >= skl_req_orbs
            
            skl_btn = discord.ui.Button(
                label=f"{skill_name} {skl_req_orbs}{emojis['orb']}", 
                style=discord.ButtonStyle.primary if has_skl_orbs else discord.ButtonStyle.secondary, 
                custom_id="btn_skl",
                disabled=not has_skl_orbs,
                row=2
            )
            async def skl_callback(interaction: discord.Interaction):
                if interaction.user.id != self.player_id: return
                # Look up the select menu component in the current view
                chosen_target = None
                for child in view.children:
                    if isinstance(child, discord.ui.Select) and child.custom_id == "target_select":
                        if child.values: 
                            chosen_target = int(child.values[0])
                
                # --- CRITICAL: EPHERMERAL TARGET CHECK ---
                if chosen_target is None:
                    await interaction.response.send_message(
                        f"❌ **Action Cancelled:** You must select a valid enemy target from the dropdown menu first!", 
                        ephemeral=True
                    )
                    return
                self.interaction = interaction
                await interaction.response.defer()
                await self.handle_player_move_selection("skl",target_idx=chosen_target)
                
            skl_btn.callback = skl_callback
            view.add_item(skl_btn)

            # ULT
            ult_info = active_unit.moves.get("ult", {})
            ult_name = ult_info.get("name", "Ultimate")
            ult_req_orbs = ult_info.get("rqmo", 5)
            has_ult_orbs = active_unit.magic_orbs >= ult_req_orbs
            
            ult_btn = discord.ui.Button(
                label=f"{ult_name} {ult_req_orbs}{emojis['orb']}", 
                style=discord.ButtonStyle.primary if has_ult_orbs else discord.ButtonStyle.secondary, 
                custom_id="btn_ult",
                disabled=not has_ult_orbs,
                row=3
            )
            async def ult_callback(interaction: discord.Interaction):
                if interaction.user.id != self.player_id: return
                # Look up the select menu component in the current view
                chosen_target = None
                for child in view.children:
                    if isinstance(child, discord.ui.Select) and child.custom_id == "target_select":
                        if child.values: 
                            chosen_target = int(child.values[0])
                
                # --- CRITICAL: EPHERMERAL TARGET CHECK ---
                if chosen_target is None:
                    await interaction.response.send_message(
                        f"❌ **Action Cancelled:** You must select a valid enemy target from the dropdown menu first!", 
                        ephemeral=True
                    )
                    return
                self.interaction = interaction
                await interaction.response.defer()
                await self.handle_player_move_selection("ult",target_idx=chosen_target)
            ult_btn.callback = ult_callback
            view.add_item(ult_btn)

        try:
            # 🟢 Directly editing the message works 100% of the time, 
            # completely bypassing deprecated interaction properties!
            await self.message.edit(embed=embed, view=view)
        except Exception as e:
            print(f"[RENDER CRASH]: {e}")

    async def _execute_enemy_automated_turn(self, enemy_attacker: CombatEntity):
        """Automates an active enemy's combat turn using the universal round counter."""
        self.last_activity_ts = time.time()
        
        # 1. Target Selector (Pick a random living ally)
        import random
        alive_allies = [idx for idx, ally in enumerate(self.allies) if ally and ally.current_hp > 0]
        if not alive_allies:
            self._check_match_over()
            return
        target_idx = random.choice(alive_allies)

        # 2. Universal Rotation: Round 1 = M1, Round 2 = Skill, Round 3 = M1...
        if self.round_cntr % 2 != 0:
            move_key = "m1"
        else:
            move_key = "skl"
            
        # Fallback check if the enemy data is missing the skill asset
        if move_key not in enemy_attacker.moves:
            move_key = "m1"

        move_data = enemy_attacker.moves[move_key]

        # Log the action header display frame
        self.log_move_execution(enemy_attacker, move_key, move_data)
        await self.render_battlefield_view(prompt_player_input=False)
        await asyncio.sleep(1.0)

        # 3. Resolve Damage Pipeline Footprint
        targets = self._get_move_targets(self.allies, target_idx, move_data.get("target", "Single"))
        
        for target in targets:
            await self._resolve_attack_pipeline(enemy_attacker, target, move_data, is_ally_attack=False)
            if self._check_match_over():
                return

        # 4. Post-Turn Upkeep
        # No counter to increment here since it relies entirely on the universal round manager!
        
        # Refresh interface display state
        await self.render_battlefield_view(prompt_player_input=False)
        await asyncio.sleep(1)

        # Step tracking pointer forward and evaluate next entity slot
        self.active_plot_idx += 1
        await self.advance_turn_state()
    
    async def _process_round_end():
        pass


    def _check_match_over(self) -> bool:
        """Evaluates team rosters and action timestamps to handle match termination."""
        # 1. Timed Inactivity Check (5 Minutes / 300 Seconds)
        import time
        if time.time() - self.last_activity_ts > 300:
            self.is_active = False
            asyncio.create_task(self._send_afk_timeout_embed())
            return True

        # Returns True if at least one character has health above zero
        allies_alive = any(a for a in self.allies if a and a.current_hp > 0)
        enemies_alive = any(e for e in self.enemies if e and e.current_hp > 0)
        
        # 2. Check if the player was wiped out (Defeat)
        if not allies_alive:
            self.combat_log = "❌💀 **DEFEAT** 💀❌"
            self.is_active = False  
            return True
            
        # 3. Check if the enemies were wiped out (Victory)
        if not enemies_alive:
            self.combat_log = "✅🎉 **VICTORY** 🎉✅"
            self.is_active = False  
            return True
            
        return False

    async def _send_afk_timeout_embed(self):
        """Sends a dedicated embed notice indicating the match closed due to inactivity."""
        embed = discord.Embed(
            title="🛑 Match closed due to inactivity💤",
            description=f"The match has been aborted since you were afk for more than 5 minutes.",
            color=discord.Color.dark_gray()
        )
        embed.set_footer(text=f"Room {self.curr_room} | Level {self.curr_level}")
        
        if self.interaction:
            await self.interaction.followup.send(embed=embed)
        else:
            await self.message.channel.send(embed=embed)