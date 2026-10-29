---
id: drustz-00deed084c41ceb59d
section: openai
order: 156
level: A
title: Monster Duel
quick: original-structured-preparation-guide · Monster Duel
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
      https://www.1point3acres.com/interview/problems/f015eda2-55c2-42c1-a27e-389cd37fbde7
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Monster Duel：一对一攻击与条件反击

## 证据边界

公开目录只给出 “Monster Duel”，没有说明它是一对一还是组队、是否含技能或属性。相关公开家族题采用“先攻击，目标存活才反击”的确定性顺序。下面将 **Duel** 解释成一对一完整练习版；属性克制、最佳攻击者和 Pokémon 技能不属于已证实约束。

## 可读题面与接口

两个怪物各有 `name、hp、attack`。每轮 A 先攻击 B；若 B 的 HP 降到 `0` 或以下，A 立即获胜；否则 B 反击 A，A 死亡则 B 获胜。双方仍存活就进入下一轮。返回胜者、完整轮数和每次伤害日志；输入对象不应被修改。

```python
def duel(a: Monster, b: Monster) -> DuelResult: ...


# Knight(hp=12, attack=5), Ogre(hp=9, attack=4)
# 第1轮后：(8,4)；第2轮 Knight 先手把 Ogre 击杀
# 输出：winner="Knight", rounds=2
```



## 解法与关键数据结构

复制两份 HP，循环执行 `damage(defender, attacker.attack)`，每一步后立刻检查死亡。可用 `Event(round, actor, target, damage, hp_after)` 保存日志。不要在轮末才统一结算，否则会错误地允许已死亡者反击。若面试官要求仅返回胜者，可用 `ceil(hp/attack)` 比较击杀回合数做 `O(1)` 推导；但需要逐击日志时仍应模拟。

## 复杂度与边界测试

设发生 `R` 次攻击，时间和日志空间均为 `O(R)`，除日志外空间 `O(1)`。测试任一方初始 HP 非正、第一击恰好击杀、反击击杀、双方相同数值、超大 HP、负攻击力，以及双方攻击力都为零。后者永不终止，应判为 draw 或拒绝输入。还要确认 A 是否固定先手；若题面有速度值，则速度相同时的 tie-break 必须明确。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/f015eda2-55c2-42c1-a27e-389cd37fbde7)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
