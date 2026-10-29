---
id: drustz-660bbaaaa672446d61
section: forum-notes
order: 265
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 1: Simple Battle Logic'
quick: '作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 1: Simple Battle Logic'
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
## Part 1: Simple Battle Logic

### Problem Requirements

Build a system with these rules:

- **Monster**: Every monster has:

A Name (string)
- Health Points (HP) - a positive integer
- Attack Power - a positive integer
- **Team**: Every team has:

A Team Name
- A list of Monsters
- **Rules of the Fight**:

Team A goes first. Teams switch turns after each attack.
- The **first living monster** on the attacking team hits the **first living monster** on the defending team.
- **Damage Math**: The defender loses HP equal to the attacker's power (`Defender HP = Defender HP - Attacker Power`).
- The attacker does NOT take damage back.
- If a monster's HP hits 0 or less, it is eliminated.
- The battle ends when all monsters on one team are eliminated.
- **Output Log**: You must print:

Every attack (who hit whom and the damage amount).
- When a monster is eliminated.
- Who won the battle.

### Class Blueprint

```python
class Monster:
    def __init__(self, name: str, health: int, attack: int):
        """
        Create a monster with a name, HP, and attack power.
        """
        pass

    def is_alive(self) -> bool:
        """Return True if health is greater than 0."""
        pass

    def take_damage(self, damage: int) -> None:
        """Lower health by the damage amount."""
        pass


class Team:
    def __init__(self, name: str, monsters: list[Monster]):
        """Create a team with a name and a list of monsters."""
        pass

    def get_first_alive(self) -> Monster | None:
        """Find the first monster that is still alive. Return None if all are dead."""
        pass

    def is_defeated(self) -> bool:
        """Return True if all monsters are eliminated."""
        pass


def battle(team_a: Team, team_b: Team) -> list[str]:
    """
    Run the battle between two teams.
    Return a list of strings describing the events.
    """
    pass
```



### Usage Example

```python
# Create monsters for Team A
dragon = Monster("Dragon", health=100, attack=25)
griffin = Monster("Griffin", health=80, attack=20)
team_a = Team("Heroes", [dragon, griffin])

# Create monsters for Team B
goblin = Monster("Goblin", health=30, attack=10)
orc = Monster("Orc", health=50, attack=15)
troll = Monster("Troll", health=70, attack=12)
team_b = Team("Monsters", [goblin, orc, troll])

# Run the battle
event_log = battle(team_a, team_b)

# The output should look like this:
# [
#     "Battle begins: Heroes vs Monsters",
#     "Dragon attacks Goblin for 25 damage. Goblin has 5 HP remaining.",
#     "Goblin attacks Dragon for 10 damage. Dragon has 90 HP remaining.",
#     "Dragon attacks Goblin for 25 damage. Goblin is eliminated!",
#     ...
#     "Battle ends: Heroes wins!"
# ]
```



### Solution Approach

```python
class Monster:
    def __init__(self, name: str, health: int, attack: int):
        self.name = name
        self.health = health
        self.attack = attack

    def is_alive(self) -> bool:
        return self.health > 0

    def take_damage(self, damage: int) -> None:
        self.health -= damage


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
        # Check if every monster is not alive
        return all(not monster.is_alive() for monster in self.monsters)


def battle(team_a: Team, team_b: Team) -> list[str]:
    events = []
    events.append(f"Battle begins: {team_a.name} vs {team_b.name}")

    # Set initial attacker and defender teams
    current_attacker = team_a
    current_defender = team_b

    # Loop until one team loses
    while not team_a.is_defeated() and not team_b.is_defeated():
        attacker = current_attacker.get_first_alive()
        defender_monster = current_defender.get_first_alive()

        # Safety check
        if attacker is None or defender_monster is None:
            break

        # Apply damage
        damage = attacker.attack
        defender_monster.take_damage(damage)

        # Record what happened
        if defender_monster.is_alive():
            events.append(
                f"{attacker.name} attacks {defender_monster.name} for {damage} damage. "
                f"{defender_monster.name} has {defender_monster.health} HP remaining."
            )
        else:
            events.append(
                f"{attacker.name} attacks {defender_monster.name} for {damage} damage. "
                f"{defender_monster.name} is eliminated!"
            )

        # Switch turns
        current_attacker, current_defender = current_defender, current_attacker

    # Check who won
    if team_b.is_defeated():
        events.append(f"Battle ends: {team_a.name} wins!")
    else:
        events.append(f"Battle ends: {team_b.name} wins!")

    return events
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
