---
id: drustz-bbf841a52b7c797b3e
section: openai
order: 54
level: A
title: Infection Spread with Immune Units and Expiring Contagiousness
quick: >-
  original-structured-preparation-guide · Infection Spread with Immune Units and
  Expiring Contagiousness
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
      https://www.1point3acres.com/interview/problems/e779b9e1-5a83-5184-b0b4-acc5d22ba660
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Infection Spread with Immune Units and Expiring Contagiousness

> **证据边界**：标题与两份本地面经共同确认“初始免疫单元”和“感染 `D` 天后失去传染性并转为免疫”。其中一份面经确认 8 邻域，但当前 UUID 是否也用 8 邻域、恢复当天先传播还是先免疫，没有公开原文；实现前应让面试官确认事件顺序。

## 状态与例子

用 `S` 表示健康、`X(age)` 表示已感染 `age` 天、`I` 表示永久免疫。`I` 不感染也不传播。以下采用一个清楚的约定：每天先让当天仍有传染性的 `X` 尝试感染邻居，所有新感染同时生效；随后令年龄达到 `D` 的旧感染格转成 `I`。例如一行 `X . I .`、`D=2`：第 1 天第二格感染，第三格始终隔断右侧。

## 算法

普通多源 BFS 只适合“感染后永久传播”；这里必须记录感染日。维护 `active` 集合和 `recover_on[day]` 事件桶：从旧 `active` 计算本日 `newly_infected`，去重后统一写入并登记其免疫日；再处理本日到期事件。若原题规定“先免疫再传播”，只需交换两个阶段，但不能混用新旧网格。

```text
spread = collect_from(active, old_state)
apply(spread); schedule_recovery(spread)
apply(recover_on[t]); active = (active ∪ spread) - recovered
```



## 复杂度与边界

事件式实现中，每格感染、免疫各一次时，时间 `O(RC·d)`、空间 `O(RC)`；若规则允许康复后再次感染，则可能振荡，必须改为逐日状态模拟并约定最大天数或检测重复状态。还要测试 `D=0/1`、全免疫、无感染源、免疫墙封闭区域，以及同一天将到期的格是否仍能传播。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/e779b9e1-5a83-5184-b0b4-acc5d22ba660)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
