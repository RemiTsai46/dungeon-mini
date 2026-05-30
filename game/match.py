import math
import asyncio
import discord
from game.soul_moves import SOUL_REGISTRY
from game.enemy_moves import ENEMY_REGISTRY
from game.effects import EFFECT_REGISTRY
from utils import db

PASSIVE_UNLOCK_LEVELS = {"p1": 40, "p2": 80, "p3": 120}
RARITY_PASSIVE_LIMITS = {"Rare": 1, "Epic": 2, "Legendary": 2, "Secret": 3}

class CombatEntity:
    def __init__(self, name: str, rarity: str, element: str, level: int, base_stats: dict, moves: list, passives: dict):
        # Core Identity
        self.name = name
        self.rarity = rarity
        self.element = element
        self.level = level
        self.magic_orbs = 0
        
        # Stat Calculations (Level 1 base stats scaling)
        self.max_hp = base_stats["hp"]
        self.current_hp = self.max_hp
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
        self.statuses = {}

    def get_calculated_dmg(self) -> int:
        """Calculates dynamic attack power including active status modifiers."""
        multiplier = 1.0
        # Future hooks for checking damage-altering active statuses can be handled here
        return int(self.base_dmg * multiplier)


class ActiveMatch:
    def __init__(self, guild_id: int, player_id: int, message):
        self.guild_id = guild_id
        self.player_id = player_id
        self.message = message
        
        # Extract the native interaction directly from the message architecture if present
        self.interaction = message.interaction if hasattr(message, "interaction") else None
        
        self.combat_logs = []
        self.round_cntr = 1
        self.is_active = True
        
        self.allies = [None, None, None, None]  
        self.enemies = [None, None, None, None]
        
        # Placeholder for dungeon enemy target initialization
        self._initialize_teams()

    def _initialize_teams(self):
        """Fills the fixed 4-slot ally team from the database and spawns enemies."""
        user_record = db.get_player_data(self.guild_id, self.player_id)
        level = getattr(user_record, "level", 1)
        
        # === SOUL INIT ===

        # get soul data
        soul_slots = getattr(user_record, "equipped_souls", [None, None, None, None])
        owned_souls = getattr(user_record, "owned_souls", {})
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
                        rarity=blueprint["rarity"],
                        element=blueprint["element"],
                        level=soul_level,
                        base_stats=blueprint["stats"],
                        moves=blueprint["moves"],
                        passives=blueprint["passives"]
                    )
                else:
                    self.allies[index] = None
            else:
                self.allies[index] = None


        # === ENEMY INIT ===

        # Placeholder loading loop: Populate up to 4 dungeon enemies for the combat challenge
        # For testing purposes, we fill slot 1 and slot 2 with test enemies
        test_enemy_blueprints = [301, 302]
        for index in range(4):
            if index < len(test_enemy_blueprints):
                enemy_soul_id = test_enemy_blueprints[index]
                blueprint = SOUL_REGISTRY.get(enemy_soul_id)
                if blueprint:
                    self.enemies[index] = CombatEntity(
                        name=f"Corrupted {blueprint['name']}",
                        rarity=blueprint["rarity"],
                        element=blueprint["element"],
                        level=10,  # Dungeon scaling level
                        base_stats=blueprint["stats"],
                        moves=blueprint["moves"],
                        passives=blueprint["passives"]
                    )
                else:
                    self.enemies[index] = None
            else:
                self.enemies[index] = None

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
        active_buff_keys = list(entity.statuses.keys())
        for status_key in active_buff_keys:
            effect_meta = EFFECT_REGISTRY.get(status_key)
            if effect_meta and effect_meta["trigger"] == event_trigger:
                # Send along the specific instance data (duration, power, etc.)
                status_instance_data = entity.statuses[status_key]
                effect_meta["func"](self, entity, status_instance_data)

    async def render_battlefield_view(self):
        """Compiles standard framework visual assets and edits them directly to Discord channels."""
        embed = discord.Embed(
            title=f"Dungeon - Level {self.round_cntr}",
            description=f"Round {self.round_cntr}",
            color=0x442200
        )
        
        # User structural frame rendering
        player_info = f"❤️ **HP:** {self.player.current_hp}/{self.player.max_hp}\n🔮 **Orbs:** {self.player.magic_orbs}"
        embed.add_field(name=f"👤 {self.player.name} (Lv. {self.player.level})", value=player_info, inline=True)
        
        # Target enemy placeholder layout frame 
        if self.enemy:
            enemy_info = f"❤️ **HP:** {self.enemy.current_hp}/{self.enemy.max_hp}"
            embed.add_field(name=f"👹 {self.enemy.name}", value=enemy_info, inline=True)
        else:
            embed.add_field(name="👹 Enemy", value="*Searching for opponent...*", inline=True)
            
        # Chronological battle logging readout parsing
        display_logs = "\n".join(self.combat_logs[-5:]) if self.combat_logs else "*The iron gates raise...*"
        embed.add_field(name="📜 Operational Log", value=display_logs, inline=False)
        
        # Dynamically push updates back utilizing the optimized channel available
        if self.interaction:
            await self.interaction.edit_original_response(embed=embed)
        else:
            await self.message.edit(embed=embed)

    async def start_loop(self):
        """Orchestrates main turn lifecycles, timeouts, processing phases, and closure cleanup."""
        self.combat_logs.append(f"⚔️ {self.player.name} stepped into the match chamber!")
        await self.render_battlefield_view()
        
        self.execute_event_pipeline(self.allies, "ON_MATCH_START")
        self.execute_event_pipeline(self.enemies, "ON_MATCH_START")        
        await self.render_battlefield_view()