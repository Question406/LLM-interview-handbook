---
id: drustz-4945eb506a6edcaad5
section: openai
order: 144
level: A
title: Pokémon Battle Simulation
quick: original-structured-preparation-guide · Pokémon Battle Simulation
companies:
  - openai
tags:
  - DrustZ
  - original-structured-preparation-guide
  - OpenAI · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/c67a473c-ca9a-49f3-a8cd-191c57a6bc3c
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Pokémon Battle Simulation：技能威力与属性克制

## 证据边界

本地原始面经直接确认题目是“宝可梦对战”，会追问技能威力不同、技能属性克制和日志输出；但没有公开完整的先手、随机数、命中率或换宠规则。下面给一个完全确定、方便测试的单挑版本；随机伤害、速度和队伍换宠只作为题面明确后的扩展。

## 可读题面与接口

每只 Pokémon 有 `name、type、hp` 和若干 `Move(name,type,power)`。给定双方轮流选择的技能序列，P1 先行动；实际伤害为 `move.power × effectiveness(move.type, defender.type)`，倍率来自表，缺省为 `1`，结果按题目指定方式取整。扣血后若防守方 `hp<=0`，立即结束且不得行动。返回胜者、回合数和日志。

```python
def simulate(
    p1: Pokemon, p2: Pokemon, actions: list[tuple[str, str]], chart: TypeChart
) -> BattleResult: ...


# Charmander(hp=20) 用 power=10 的 fire 技能攻击 grass 的 Bulbasaur
# 若倍率为 2，日志记录 damage=20，Bulbasaur fainted，winner="Charmander"
```



## 解法与关键数据结构

用哈希表按技能名查 `Move`，另用 `(attack_type, defend_type)` 二元组查倍率。`take_turn` 完成技能校验、算伤害、截断显示 HP 和生成 `Event`；主循环只负责交替玩家并在每次攻击后检查结束。倍率建议存成有理数 `(numerator, denominator)`，统一执行整数除法，避免浮点误差。日志使用事件对象，最后转成 f-string。

## 复杂度与边界测试

预先建立技能索引后，每回合 `O(1)`，总时间和日志空间为 `O(T)`，类型表空间 `O(P)`。测试未知技能、同属性、无克制项、半伤取整、伤害等于剩余 HP、已昏厥者不能行动、动作列表提前耗尽、零威力造成无限战斗、双方同名技能，以及调用后是否应保留原 Pokémon。若原题加入速度或换宠，必须先补 tie-break 再改状态机。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/c67a473c-ca9a-49f3-a8cd-191c57a6bc3c)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
