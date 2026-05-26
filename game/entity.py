class CombatEntity:
    def __init__(self, slot_id: int, entity_id: int, blueprint: dict):
        self.slot_id = slot_id        # 0 to 3 (Plot 1 to 4)
        self.entity_id = entity_id    # e.g., 301 for Caren
        self.name = blueprint["name"]
        
        # Base Stats
        stats = blueprint["stats"]
        self.max_hp = stats["hp"]
        self.current_hp = stats["hp"]
        self.dmg = stats["dmg"]
        self.cc = stats["cc"]
        self.cd = stats["cd"]
        self.dfs = stats["dfs"]
        
        # Skill references & Passives
        self.moves = blueprint["moves"]
        self.passives = blueprint["passives"]
        
        # Active combat states
        self.statuses = {} 
        self.magic_orbs = 0 # Every entity tracks its own resource pool