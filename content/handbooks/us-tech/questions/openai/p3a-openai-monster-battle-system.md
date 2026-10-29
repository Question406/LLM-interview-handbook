---
id: p3a-openai-monster-battle-system
section: openai
order: 608
level: A
title: OpenAI：怪兽战斗：基础规则、属性克制与目标策略
quick: >-
  把伤害计算、目标选择和轮次主循环分别写成函数，分阶段加规则时只改对应部分。每次攻击记录双方、伤害和剩余血量，便于逐回合核对；smart
  只选择当前伤害最大的目标，是贪心策略，不能保证整场最优。
companies:
  - openai
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - OpenAI
  - 题面补全 2026-10-27
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: 1Point3Acres · OpenAI · monster-battle-system
    url: >-
      https://www.1point3acres.com/interview/problems/company/openai/monster-battle-system
    type: secondary
---

## 题目描述

实现一个确定性的回合制怪物战斗模拟器，返回胜者与完整攻击日志。

以下 interface 与 edge-case behavior 是本手册重构练习的约定。假定输入满足所述合法范围。

### 接口、输入与输出要求

`battle(team0,team1,effect=None,smart=False)` 返回 `(winner,logs)`，不修改输入。每个怪物为含 name、hp、attack、element 的字典，初始 hp、attack 为正。队伍 0 先攻，双方交替，每回合由己方列表中首个存活怪物攻击一次。

默认攻击敌方首个存活怪物；smart=True 时选择本次立即伤害最大的存活目标，同伤害选队伍顺序靠前者。伤害为 `max(1,floor(attack*倍率))`，倍率来自 effect[(攻击者属性,目标属性)]，缺省为 1。目标剩余 hp 最低为 0，死亡怪物不再行动或受选。

一队全部死亡时结束，winner 为 0 或 1；两队初始均空时为 None。日志逐次记录 `(攻击者名,目标名,伤害,目标剩余hp)`。每队不超过 20 个怪物，初始 hp 不超过 100。

### 示例

```text
team0=[{name:"A",hp:3,attack:2,element:"fire"}]
team1=[{name:"B",hp:2,attack:1,element:"water"}]，effect 缺省。
返回 winner=0，logs=[("A","B",2,0)]。
```

## 解题思路与参考答案

我会把伤害、选目标和战斗循环分开实现，先按基础规则跑通，再加属性与策略。比如火克水只影响伤害函数，smart 选目标只改选择函数，轮次和日志就能继续复用。

实现一个回合制的双队怪兽战斗模拟，分阶段加需求：先是基础的轮流攻击，再加入属性克制，最后加入「智能选目标」的规则。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理。下面的接口、约束和测试是手册补的练习约定。

## 思路

分阶段加需求的题，代码结构比算法更重要。把三件事拆成独立的函数：

- 伤害计算：输入攻击者和目标，输出伤害值。加属性克制时只改这里。
- 选目标策略：输入攻击者和存活的敌人列表，输出目标。加智能策略时只改这里。
- 战斗主循环：决定谁行动、更新生命值、记录日志、判断结束。

这样每加一个阶段只动一个函数，主循环和日志格式不受影响。日志记下每次攻击的双方、伤害和剩余血量，结果和预期不一致时能快速定位是哪一回合出了差错。

要和面试官确认的规则：谁先手，每回合是一只怪兽行动还是全队行动，并列目标怎么选，两队同时全灭算谁赢，有没有复活。

「智能」策略要先问清楚目标是什么。每次打伤害最高的目标只是一个贪心规则，不能说它是全局最优的战斗策略。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `battle(team0, team1, effect=None, smart=False) -> (winner, logs)`：每只怪兽是 `{"name", "hp", "attack", "element"}`，`hp` 和 `attack` 初始为正整数，否则抛 `ValueError`。
- 两队轮流行动，`team0` 先手。每回合由己方第一只存活的怪兽攻击一次。
- 普通模式攻击敌方第一只存活的怪兽；`smart=True` 时攻击这一下伤害最高的目标，并列时选靠前的。
- 伤害 = $\max(1, \lfloor attack \times m \rfloor)$，其中 $m$ 是 `effect[(攻击者属性, 目标属性)]`，没配置时为 1。
- 死亡的怪兽不再行动，也不能被选为目标，没有复活。一队全灭时结束，返回赢家（0 或 1；两队一开始都为空时是 `None`）和日志，日志每项是 `(攻击者, 目标, 伤害, 目标剩余 hp)`。不修改输入。
- 每队最多 20 只，`hp` 不超过 100。

### 输入输出示例

```text
team0 = [A: hp=3, attack=2, fire]
team1 = [B: hp=2, attack=1, water]
battle(team0, team1) -> (0, [("A", "B", 2, 0)])     # A 先手，一击打死 B
```

如果 `team1` 里还有一只 water 属性的 D，并且 `effect = {("fire", "water"): 2}`、`smart=True`，A 会优先打 D，因为对 D 的伤害是 4。

### 解题思路与正确性

`compute_damage`、`choose_target` 和主循环互相独立。加新的克制规则或新的选目标策略时，不需要改轮次和日志的逻辑。

每次攻击至少造成 1 点伤害，没有复活，所以总攻击次数不会超过两队初始血量之和，循环一定结束。开头做了深拷贝，同一组输入可以反复用不 on-policy 跑，结果可以复现。

### 完整参考实现（Python 3）

```python
from copy import deepcopy


def compute_damage(attacker, target, effect):
    """伤害 = attack × 属性倍率，向下取整，至少为 1。没配置的属性组合倍率为 1。"""
    multiplier = effect.get((attacker["element"], target["element"]), 1)
    return max(1, int(attacker["attack"] * multiplier))


def choose_target(attacker, targets, effect, smart):
    """普通模式打第一个存活的敌人；smart 模式打这一下伤害最高的，并列取靠前的。"""
    if not smart:
        return targets[0]
    return max(
        targets, key=lambda target: compute_damage(attacker, target, effect)
    )  # max 并列时返回第一个


def alive(team):
    return [monster for monster in team if monster["hp"] > 0]


def battle(team0, team1, effect=None, smart=False):
    """两队轮流攻击，team0 先手，直到一方全灭。返回 (winner, logs)，不修改输入。

    winner 是 0、1，或两队一开始都为空时的 None；
    logs 每项是 (攻击者, 目标, 伤害, 目标剩余 hp)。
    """
    teams = [deepcopy(team0), deepcopy(team1)]
    effect = effect or {}
    for team in teams:
        for monster in team:
            if monster["hp"] <= 0 or monster["attack"] <= 0:
                raise ValueError(f"hp and attack must be positive: {monster!r}")

    logs = []
    side = 0
    while alive(teams[0]) and alive(teams[1]):
        attacker = alive(teams[side])[0]
        target = choose_target(attacker, alive(teams[1 - side]), effect, smart)
        damage = compute_damage(attacker, target, effect)
        target["hp"] = max(0, target["hp"] - damage)
        logs.append((attacker["name"], target["name"], damage, target["hp"]))
        side = 1 - side

    if alive(teams[0]):
        winner = 0
    elif alive(teams[1]):
        winner = 1
    else:
        winner = None
    return winner, logs
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert battle(team_a, team_b) == (0, [("A", "B", 2, 0)])` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
def monster(name, hp, attack, element):
    return {"name": name, "hp": hp, "attack": attack, "element": element}


# 先手一击打死对方，输入不被修改
team_a = [monster("A", 3, 2, "fire")]
team_b = [monster("B", 2, 1, "water")]
assert battle(team_a, team_b) == (0, [("A", "B", 2, 0)])
assert team_a[0]["hp"] == 3

# 一方为空，另一方直接获胜；两方都空则没有赢家
assert battle([], team_b)[0] == 1
assert battle([], []) == (None, [])

# smart 模式选伤害最高的目标：火克水，打 D 是 4 点，打 C 是 2 点
team_c = [monster("C", 1, 1, "wood"), monster("D", 2, 1, "water")]
winner, logs = battle(team_a, team_c, {("fire", "water"): 2}, smart=True)
assert logs[0][1] == "D"

# 普通模式打第一个存活者；倍率很小时伤害至少为 1
winner, logs = battle(team_a, team_c, {("fire", "wood"): 0.1})
assert logs[0] == ("A", "C", 1, 0)

# 非法输入
try:
    battle([monster("E", 0, 1, "fire")], team_b)
except ValueError:
    pass
else:
    raise AssertionError("hp 0 should be rejected")
```

### 复杂度与追问

设每队最多 M 只怪兽、两队初始总血量为 H。总攻击次数不超过 H；每次攻击要找存活的怪兽、为 smart 模式扫一遍敌人，都是 O(M)，所以总时间 O(H·M)，日志空间 O(H)。

- smart 策略是最优的吗？不是。它只看这一下打谁伤害最高，可能把高伤害浪费在一只快死的怪兽上。要求整场胜率最优，需要搜索双方之后的行动，用当前所有怪兽的血量作为状态做记忆化。状态数随队伍规模指数增长，只适合小规模。
- 要加速度属性决定出手顺序呢？把「谁行动」也抽成一个函数，比如每回合按速度从高到低排列所有存活怪兽依次行动，主循环其余部分不变。
