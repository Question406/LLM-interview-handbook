---
id: drustz-efdb2f99edbca87a63
section: openai
order: 105
level: A
title: Plant Infection Simulation (Multi-part)
quick: >-
  original-structured-preparation-guide · Plant Infection Simulation
  (Multi-part)
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
      https://www.1point3acres.com/interview/problems/d5566b1b-8678-45b4-ae3a-6d3af9afd9d9
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Plant Infection Simulation：面向多问的实现结构

> **已佐证内容**：植物版面经明确使用 `X / . / I`，基础传播看 8 个邻居，`I` 永久免疫，感染植物在 `D` 天后康复并免疫；还问过超大矩阵。其他汇编提到死亡规则，但没有证据证明当前 UUID 一定包含它，因此只留扩展接口。

## 建议的数据结构

保存 `state[r][c]` 和 `infected_at[r][c]`，另维护 `active`（仍可传播的感染格）、`recover_on[day]`（当天转免疫的格）与 `frontier`（上日发生变化的格）。不要把感染年龄编码进字符后反复解析。

以 `X..`、8 邻域、`D=2` 为例：第 1 天第二格感染；第 2 天第三格感染，同时初始格按约定转 `I`。若题面规定到期先免疫，则初始格第 2 天不能再传播，所以必须显式写出每日阶段顺序。

## 每日流程

1. 从旧 `active` 收集所有仍为 `.` 的邻居，放入集合去重；
2. 一次性把这些格改为 `X`，记录感染日和恢复日；
3. 处理当天 `recover_on`，转成 `I` 并从 `active` 删除；
4. 根据题目要求，在“无新感染”或“无 active 感染”时停止。

```text
new = union(susceptible_neighbors(x) for x in active)
commit(new); schedule(new, day + D); recover(due_today)
```



大而稀疏的矩阵可用坐标集合和事件桶；分块存储时只交换 tile 边界。

## 复杂度与边界

不可再感染时每格和每条邻接边只处理常数次，时间、空间均 `O(RC)`；一般逐日模拟为 `O(T·RC)`。覆盖 `D=0/1`、全 `I`、无 `X`、免疫隔断、到期与传播同日、不同停止条件。死亡规则只有在原题明确给出时再实现。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/d5566b1b-8678-45b4-ae3a-6d3af9afd9d9)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
