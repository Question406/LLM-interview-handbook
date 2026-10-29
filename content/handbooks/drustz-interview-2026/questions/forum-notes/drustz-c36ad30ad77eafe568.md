---
id: drustz-c36ad30ad77eafe568
section: forum-notes
order: 266
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 2: Adding Elemental Types'
quick: '作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 2: Adding Elemental Types'
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - 面经整理与回答建议
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md
    type: primary
---
## Part 2: Adding Elemental Types

### Problem Requirements

Update the system to include **monster types**. Certain types are strong or weak against others.

- **Monster Types**: Give every monster a type (like Fire, Water, Grass, Electric).
- **Type Logic**:

**Double Damage (2x)**: Strong matchups.
- **Half Damage (0.5x)**: Weak matchups.
- **Normal Damage (1x)**: Neutral matchups.
- **Type Chart**:

Fire beats Grass (2x)
- Fire is weak to Water (0.5x)
- Water beats Fire (2x)
- Water is weak to Grass (0.5x)
- Grass beats Water (2x)
- Grass is weak to Fire (0.5x)
- Electric beats Water (2x)
- Everything else is normal (1x)
- **Order**: The attack order stays the same (first alive vs. first alive).

### Class Updates

```python
from enum import Enum


class MonsterType(Enum):
    FIRE = "Fire"
    WATER = "Water"
    GRASS = "Grass"
    ELECTRIC = "Electric"


class Monster:
    def __init__(self, name: str, health: int, attack: int, monster_type: MonsterType):
        self.name = name
        self.health = health
        self.attack = attack
        self.monster_type = monster_type

    def calculate_damage(self, defender: 'Monster') -> int:
        """Calculate how much damage to deal based on types."""
        pass
```



### Usage Example

```python
# Create monsters with types
fire_dragon = Monster(
    "FireDragon", health=100, attack=20, monster_type=MonsterType.FIRE
)
water_serpent = Monster(
    "WaterSerpent", health=80, attack=15, monster_type=MonsterType.WATER
)

# Math:
# FireDragon vs WaterSerpent: 20 * 0.5 = 10 damage (Weak)
# WaterSerpent vs FireDragon: 15 * 2.0 = 30 damage (Strong)
```



### Solution Details

```python
from enum import Enum


class MonsterType(Enum):
    FIRE = "Fire"
    WATER = "Water"
    GRASS = "Grass"
    ELECTRIC = "Electric"


# Dictionary mapping (Attacker Type, Defender Type) to a multiplier
TYPE_CHART = {
    (MonsterType.FIRE, MonsterType.GRASS): 2.0,
    (MonsterType.FIRE, MonsterType.WATER): 0.5,
    (MonsterType.WATER, MonsterType.FIRE): 2.0,
    (MonsterType.WATER, MonsterType.GRASS): 0.5,
    (MonsterType.GRASS, MonsterType.WATER): 2.0,
    (MonsterType.GRASS, MonsterType.FIRE): 0.5,
    (MonsterType.ELECTRIC, MonsterType.WATER): 2.0,
}


class Monster:
    def __init__(self, name: str, health: int, attack: int, monster_type: MonsterType):
        self.name = name
        self.health = health
        self.attack = attack
        self.monster_type = monster_type

    def is_alive(self) -> bool:
        return self.health > 0

    def take_damage(self, damage: int) -> None:
        self.health -= damage

    def calculate_damage(self, defender: 'Monster') -> int:
        """Return damage adjusted by the type chart."""
        multiplier = TYPE_CHART.get(
            (self.monster_type, defender.monster_type),
            1.0,  # Default to 1.0 if the pair isn't in the chart
        )
        return int(self.attack * multiplier)


class Team:
    def __init__(self, name: str, monsters: list[Monster]):
        self.name = name
        self.monsters = monsters

    def get_first_alive(self) -> Monster | None:
        for monster in self.monsters:
            if monster.is_alive():
                return monster
        return None

    def is_defeated(self) -> bool:
        return all(not monster.is_alive() for monster in self.monsters)


def battle(team_a: Team, team_b: Team) -> list[str]:
    events = []
    events.append(f"Battle begins: {team_a.name} vs {team_b.name}")

    current_attacker = team_a
    current_defender = team_b

    while not team_a.is_defeated() and not team_b.is_defeated():
        attacker = current_attacker.get_first_alive()
        defender_monster = current_defender.get_first_alive()

        if attacker is None or defender_monster is None:
            break

        # Calculate damage using the new method
        damage = attacker.calculate_damage(defender_monster)
        defender_monster.take_damage(damage)

        # Create a text note for effectiveness
        base_damage = attacker.attack
        if damage > base_damage:
            effectiveness = " (Super effective!)"
        elif damage < base_damage:
            effectiveness = " (Not very effective...)"
        else:
            effectiveness = ""

        # Log the event
        if defender_monster.is_alive():
            events.append(
                f"{attacker.name} attacks {defender_monster.name} for {damage} damage{effectiveness}. "
                f"{defender_monster.name} has {defender_monster.health} HP remaining."
            )
        else:
            events.append(
                f"{attacker.name} attacks {defender_monster.name} for {damage} damage{effectiveness}. "
                f"{defender_monster.name} is eliminated!"
            )

        current_attacker, current_defender = current_defender, current_attacker

    if team_b.is_defeated():
        events.append(f"Battle ends: {team_a.name} wins!")
    else:
        events.append(f"Battle ends: {team_b.name} wins!")

    return events
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
