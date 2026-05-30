async def caren_ult_buff(match, entity, context_payload=None):
    """
    [ID: 3014] Caren's Pyro Fury Action Modifier.
    Injects the 10% damage multiplier directly into the temporary action buffs map.
    """
    # Simply assign the flat value directly without running registry checks
    entity.action_buffs[3014] = 0.10
    match.combat_logs = f"🔥 **{entity.name}** was empowered by Pyro Fury! Next strike deals +10% damage."


async def caren_p1_rage_mode(match, entity, context_payload=None):
    """
    [ID: 3011] Caren's Passive 1: Rage Mode.
    Gives +1 extra Magic Orb up to a maximum resource cap of 10.
    """
    entity.magic_orbs = min(10, entity.magic_orbs + 1)
    match.combat_logs = f"🔥 **{entity.name}** triggered [Rage Mode]! Gained +1 extra Magic Orb."

# Central Function Lookups used by your pipeline executors
EFFECT_REGISTRY = {
    3011: {"name": "Rage Mode", "trigger": "AFTER_ULT", "func": caren_p1_rage_mode},
    3014: {"name": "Pyro Fury Boost", "trigger": "ON_ULT_CAST", "func": caren_ult_buff}
}
