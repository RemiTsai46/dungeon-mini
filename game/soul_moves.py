SOUL_REGISTRY = {
    301: {
        "name": "Caren",
        "rarity": "Rare",
        "element": "Fire",
        "class": "Warrior",
        
        # Base Stats (Level 1)
        "stats": {
            "hp": 50,
            "dmg": 10,
            "cc": 0.05, # 5%
            "cd": 1.2, # 120%
            "dfs": 0.0 # 0%
        },
        
        # Moves Kit
        "moves": {
            "m1": {
                "name": "Fire Slash",
                "description": "Slash an enemy with a burning sword",
                "target": "Single",
                "element": "Physical",
                "multi": 1.0,
                "rqmo": 0
            },
            "skl": {
                "name": "Flame Spin",
                "description": "Release a fire spin attack following a charge of power",
                "target": "Extended",
                "element": "Fire",
                "multi": 1.5,
                "rqmo": 3
            },
            "ult": {
                "name": "Pyro Fury",
                "description": "Smash the ground using a flaming blade",
                "target": "Extended",
                "element": "Fire",
                "multi": 2.0,
                "rqmo": 5,
                "buff": {"type": "dmg_boost", "value": 0.10}
            }
        },
        
        # Passives
        "passives": {
            "p1": {
                "id": "rage_mode",
                "name": "Rage Mode",
                "description": "Go into a fury in the flames. Magic orb gain +1 after using ult",
                "trigger": "after_ult"
            },
            "p2": None,
            "p3": None
        }
    }
}