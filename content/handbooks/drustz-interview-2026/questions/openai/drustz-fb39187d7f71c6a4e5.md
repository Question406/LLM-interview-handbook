---
id: drustz-fb39187d7f71c6a4e5
section: openai
order: 72
level: A
title: Monster Fighting (Multi-part)
quick: original-structured-preparation-guide · Monster Fighting (Multi-part)
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
      https://www.1point3acres.com/interview/problems/14fe459e-0891-4c3a-a60a-2ed0915c78f0
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Monster Fighting（Multi-part）：可扩展的组队战斗

## 证据边界

标题确认它是多阶段 Monster Fighting。本地同家族资料给出“基础组队战 → 属性克制 → 选择预期伤害最大的攻击者”，另一公开版本却是“主攻 → 死亡检查 → 存活才反击”。两套回合顺序不能混成会员原文。下面采用第一套作为完整练习版，并把顺序封装为规则对象。

## 可读题面与接口

两队各有一个有序怪物列表；怪物含 `name、hp、attack、type`。基础版双方交替行动，攻击方第一个存活怪物攻击防守方第一个存活怪物，`hp<=0` 淘汰，某队全灭时结束。第二问加入 `(攻击属性, 防守属性) -> 倍率`；第三问改为从攻击队存活怪物中选择实际伤害最大者，同伤害取列表靠前者。输出胜者和逐次事件日志。

```python
def fight(
    team_a: list[Monster],
    team_b: list[Monster],
    type_chart: dict[tuple[str, str], float],
) -> BattleResult: ...


# A=[FireFox(hp=20, atk=8, fire)], B=[Leaf(hp=12, atk=4, grass)]
# fire 对 grass 为 2 倍：第一击造成 16，返回 winner="A" 并记录淘汰日志
```



## 解法与关键数据结构

`Monster` 负责存活判断、扣血和伤害计算；`Team` 维护原顺序及首个存活位置；`Battle` 只推进状态机和产生日志。属性表用哈希表，未命中默认 `1`。第三问每回合线性扫描攻击队，使用严格 `>` 更新最佳者，天然保留 tie-break。务必复制输入，避免一次测试污染下一次。

## 复杂度与边界测试

设共进行 `R` 次攻击、两队最多 `N` 个怪物。基础版用游标为 `O(R+N)`；每次选最佳攻击者为 `O(RN)`；空间含日志为 `O(R+N)`。测试空队、初始 `hp<=0`、伤害刚好清零、倍率后取整、最佳伤害并列、连续多个已死亡成员、未知属性，以及所有存活者伤害为零导致无法结束；最后一种应拒绝输入或返回 draw。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/14fe459e-0891-4c3a-a60a-2ed0915c78f0)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
