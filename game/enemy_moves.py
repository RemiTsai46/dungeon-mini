ENEMY_REGISTRY = {
    # === 101-105 SLIMES ===
    101: {
        "name": "Slime",
        "emoji": "<:slime:1510259151136362637>",
        "type": "Normal",
        "element": "Normal",
        "stats": {"hp": 30, "dmg": 5, "cc": 0.00, "cd": 1.00, "dfs": 0.00},
        "moves": {
            "m1": {"name": None, "target": "Single", "multiplier": 1.0, "element": "Normal"},
            "skl": {"name": None, "target": "Extended", "multiplier": 1.3, "element": "Normal"}
        },
        "passives": {"p1": None, "p2": None, "p3": None}
    },
    102: {
        "name": "Fire Slime",
        "emoji": "<:fire_slime:1510259137890746398>",
        "type": "Normal",
        "element": "Fire",
        "stats": {"hp": 50, "dmg": 10, "cc": 0.00, "cd": 1.00, "dfs": 0.00},
        "moves": {
            "m1": {"name": None, "target": "Single", "multiplier": 1.0, "element": "Normal"},
            "skl": {"name": None, "target": "Extended", "multiplier": 1.5, "element": "Fire"}
        },
        "passives": {"p1": None, "p2": None, "p3": None}
    },
    103: {
        "name": "Ice Slime",
        "emoji": "<:ice_slime:1510259149387333652>",
        "type": "Normal",
        "element": "Ice",
        "stats": {"hp": 50, "dmg": 10, "cc": 0.00, "cd": 1.00, "dfs": 0.00},
        "moves": {
            "m1": {"name": None, "target": "Single", "multiplier": 1.0, "element": "Normal"},
            "skl": {"name": None, "target": "Extended", "multiplier": 1.5, "element": "Ice"}
        },
        "passives": {"p1": None, "p2": None, "p3": None}
    },
    104: {
        "name": "Wind Slime",
        "emoji": "<:wind_slime:1510259157343666216>",
        "type": "Normal",
        "element": "Wind",
        "stats": {"hp": 50, "dmg": 10, "cc": 0.00, "cd": 1.00, "dfs": 0.00},
        "moves": {
            "m1": {"name": None, "target": "Single", "multiplier": 1.0, "element": "Normal"},
            "skl": {"name": None, "target": "Extended", "multiplier": 1.5, "element": "Wind"}
        },
        "passives": {"p1": None, "p2": None, "p3": None}
    },
    105: {
        "name": "Electric Slime",
        "emoji": "<:electric_slime:1510259127027499029>",
        "type": "Normal",
        "element": "Electric",
        "stats": {"hp": 50, "dmg": 10, "cc": 0.00, "cd": 1.00, "dfs": 0.00},
        "moves": {
            "m1": {"name": None, "target": "Single", "multiplier": 1.0, "element": "Normal"},
            "skl": {"name": None, "target": "Extended", "multiplier": 1.5, "element": "Electric"}
        },
        "passives": {"p1": None, "p2": None, "p3": None}
    },

    # === 201 ELITE SLIME ===
    201: {
        "name": "Elemental Slime",
        "emoji": "<:elemental_slime:1510259128981917726>",
        "type": "Elite",
        "element": "Normal", # Multi-element dynamic target handler
        "stats": {"hp": 100, "dmg": 15, "cc": 0.05, "cd": 1.20, "dfs": 0.00},
        "moves": {
            "m1": {"name": None, "target": "Extended", "multiplier": 1.0, "element": "Normal"},
            "skl": {"name": None, "target": "AoE", "multiplier": 1.5, "element": "All"}
        },
        "passives": {"p1": 9001, "p2": None, "p3": None} # Linked to end-of-round self-heal logic hook
    },

    # === 106-110 GOBLIN FIGHTERS ===
    106: {
        "name": "Goblin Fighter",
        "emoji": "<:goblin_fighter:1510259141510172752>",
        "type": "Normal",
        "element": "Normal",
        "stats": {"hp": 80, "dmg": 12, "cc": 0.00, "cd": 1.20, "dfs": 0.00},
        "moves": {
            "m1": {"name": None, "target": "Single", "multiplier": 0.8, "element": "Normal"},
            "skl": {"name": None, "target": "Extended", "multiplier": 1.3, "element": "Normal"}
        },
        "passives": {"p1": None, "p2": None, "p3": None}
    },
    107: {
        "name": "Fire Goblin Fighter",
        "emoji": "<:fire_goblin_fighter:1510259133721612400>",
        "type": "Normal",
        "element": "Fire",
        "stats": {"hp": 100, "dmg": 15, "cc": 0.00, "cd": 1.20, "dfs": 0.00},
        "moves": {
            "m1": {"name": None, "target": "Single", "multiplier": 0.8, "element": "Normal"},
            "skl": {"name": None, "target": "Extended", "multiplier": 1.5, "element": "Fire"}
        },
        "passives": {"p1": None, "p2": None, "p3": None}
    },
    108: {
        "name": "Ice Goblin Fighter",
        "emoji": "<:ice_goblin_fighter:1510259147441180802>",
        "type": "Normal",
        "element": "Ice",
        "stats": {"hp": 100, "dmg": 15, "cc": 0.00, "cd": 1.20, "dfs": 0.00},
        "moves": {
            "m1": {"name": None, "target": "Single", "multiplier": 0.8, "element": "Normal"},
            "skl": {"name": None, "target": "Extended", "multiplier": 1.5, "element": "Ice"}
        },
        "passives": {"p1": None, "p2": None, "p3": None}
    },
    109: {
        "name": "Wind Goblin Fighter",
        "emoji": "<:wind_goblin_fighter:1510259155380998325>",
        "type": "Normal",
        "element": "Wind",
        "stats": {"hp": 100, "dmg": 15, "cc": 0.00, "cd": 1.20, "dfs": 0.00},
        "moves": {
            "m1": {"name": None, "target": "Single", "multiplier": 0.8, "element": "Normal"},
            "skl": {"name": None, "target": "Extended", "multiplier": 1.5, "element": "Wind"}
        },
        "passives": {"p1": None, "p2": None, "p3": None}
    },
    110: {
        "name": "Electric Goblin Fighter",
        "emoji": "<:electric_goblin_fighter:1510259124691271811>",
        "type": "Normal",
        "element": "Electric",
        "stats": {"hp": 100, "dmg": 15, "cc": 0.00, "cd": 1.20, "dfs": 0.00},
        "moves": {
            "m1": {"name": None, "target": "Single", "multiplier": 0.8, "element": "Normal"},
            "skl": {"name": None, "target": "Extended", "multiplier": 1.5, "element": "Electric"}
        },
        "passives": {"p1": None, "p2": None, "p3": None}
    },

    # === 111-115 GOBLIN ARCHERS ===
    111: {
        "name": "Goblin Archer",
        "emoji": "<:goblin_archer:1510259139559952424>",
        "type": "Normal",
        "element": "Normal",
        "stats": {"hp": 80, "dmg": 15, "cc": 0.05, "cd": 1.20, "dfs": 0.00},
        "moves": {
            "m1": {"name": None, "target": "Single", "multiplier": 1.0, "element": "Normal"},
            "skl": {"name": None, "target": "Extended", "multiplier": 1.5, "element": "Normal"}
        },
        "passives": {"p1": None, "p2": None, "p3": None}
    },
    112: {
        "name": "Fire Goblin Archer",
        "emoji": "<:fire_goblin_archer:1510259131959869600>",
        "type": "Normal",
        "element": "Fire",
        "stats": {"hp": 100, "dmg": 15, "cc": 0.05, "cd": 1.20, "dfs": 0.00},
        "moves": {
            "m1": {"name": None, "target": "Single", "multiplier": 1.0, "element": "Normal"},
            "skl": {"name": None, "target": "Extended", "multiplier": 1.5, "element": "Fire"}
        },
        "passives": {"p1": None, "p2": None, "p3": None}
    },
    113: {
        "name": "Ice Goblin Archer",
        "emoji": "<:ice_goblin_archer:1510259144983314563>",
        "type": "Normal",
        "element": "Ice",
        "stats": {"hp": 100, "dmg": 15, "cc": 0.05, "cd": 1.20, "dfs": 0.00},
        "moves": {
            "m1": {"name": None, "target": "Single", "multiplier": 1.0, "element": "Normal"},
            "skl": {"name": None, "target": "Extended", "multiplier": 1.5, "element": "Ice"}
        },
        "passives": {"p1": None, "p2": None, "p3": None}
    },
    114: {
        "name": "Wind Goblin Archer",
        "emoji": "<:wind_goblin_archer:1510259153048699042>",
        "type": "Normal",
        "element": "Wind",
        "stats": {"hp": 100, "dmg": 15, "cc": 0.05, "cd": 1.20, "dfs": 0.00},
        "moves": {
            "m1": {"name": None, "target": "Single", "multiplier": 1.0, "element": "Normal"},
            "skl": {"name": None, "target": "Extended", "multiplier": 1.5, "element": "Wind"}
        },
        "passives": {"p1": None, "p2": None, "p3": None}
    },
    115: {
        "name": "Electric Goblin Archer",
        "emoji": "<:electric_goblin_archer:1510259121855664249>",
        "type": "Normal",
        "element": "Electric",
        "stats": {"hp": 100, "dmg": 15, "cc": 0.05, "cd": 1.20, "dfs": 0.00},
        "moves": {
            "m1": {"name": None, "target": "Single", "multiplier": 1.0, "element": "Normal"},
            "skl": {"name": None, "target": "Extended", "multiplier": 1.5, "element": "Electric"}
        },
        "passives": {"p1": None, "p2": None, "p3": None}
    }
}