from entity import CombatEntity


SOUL_REGISTRY = {
    301: {  # Unique Character ID
        "name": "Caren",
        "rarity": "Rare",
        "element": "Fire",
        "class": "Warrior",
        "stats": {"hp": 50, "dmg": 10, "cc": 0.05, "cd": 1.20, "dfs": 0.00},
        "moves": {
            "m1": {"name": "Fire Slash", "target_type": "Single", "multiplier": 1.0, "rqmo": 0},
            "skl": {"name": "Flame Spin", "target_type": "Extended", "multiplier": 1.5, "rqmo": 3},
            "ult": {"name": "Pyro Fury", "target_type": "Extended", "multiplier": 2.0, "rqmo": 5}
        },
        "passives": {
            "p1": {"name": "Rage mode", "trigger": "after_ult", "effect": {"mo_gain": 1}}
        }
    }
}