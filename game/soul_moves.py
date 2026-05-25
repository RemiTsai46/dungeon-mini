from abc import ABC, abstractmethod

class CombatEntity(ABC):
    def __init__(self, id: int, name:str, level: int, grade: int, rarity: int):
        self.id = id
        self.name = name
        self.level = level
        self.grade = grade
        self.rarity = rarity

    @abstractmethod
    def m1(self, target): 
        """Standard basic attack."""
        pass

    @abstractmethod
    def skill(self, target):
        """Cooldown-based or energy-based tactical skill."""
        pass

    def ult(self, targets: list): 
        """
        Default Ultimate behavior. Most enemies don't have one, 
        so we default to doing nothing. Characters will override this.
        """
        return f"{self.name} does not have an Ultimate ability!"

    @property
    @abstractmethod
    def passives(self) -> list:
        """Returns a list of passive function behaviors or identifiers."""
        pass

class Caren(CombatEntity):
    def __init__(self, level: int, grade: int):
        # We hardcode the ID (101) and Name ("Ember Knight") right here!
        super().__init__(character_id=101, name="Ember Knight", level=level, grade=grade)

    def m1(self, target): return f"{self.name} slashes!"
    def skill(self, target): return f"{self.name} uses Flame Burst!"