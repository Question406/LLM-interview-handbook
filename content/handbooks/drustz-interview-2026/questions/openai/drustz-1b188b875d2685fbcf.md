---
id: drustz-1b188b875d2685fbcf
section: openai
order: 107
level: A
title: >-
  Optimal Turn-Based Monster Battle Simulation with Ordering and Revival
  Decisions
quick: >-
  original-structured-preparation-guide · Optimal Turn-Based Monster Battle
  Simulation with Ordering and Revival Decisions
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
      https://www.1point3acres.com/interview/problems/30f3afa1-b8ac-4730-8eaa-11fdb969077b
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Monster Battle：排序、决策与 Revival

> 公开标题确认有出战顺序和复活决策，但精确伤害、技能和胜负规则未公开。旧正文只有基础回合战斗，下面给出可配置状态搜索。

## 状态建模

状态至少包含双方存活集合、当前上场怪物及 HP、尚未部署顺序、剩余复活次数、当前回合和技能 cooldown。所有字段必须可序列化成不可变 key，用于 memoization。

```text
solve(state):
  if terminal: return win_probability / best_score
  enumerate legal actions:
    attack, switch, choose next monster, revive(target, timing)
  recurse to next state
  choose the action maximizing the objective
```



随机伤害形成 chance node，按概率加权；若敌方也最优行动，则变为 minimax。保存 best action 可恢复策略。revival 资源必须单调减少，否则需要检测循环。

## 复杂度与边界

时间 `O(|reachable states| × legal actions)`，最坏随队伍排列和复活次数指数增长。覆盖同时死亡、平局、零复活、复活 HP、死亡触发技能、概率和、相同怪物去重和无限循环。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/30f3afa1-b8ac-4730-8eaa-11fdb969077b)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
