---
id: drustz-cb316da9b44cfe1fba
section: openai
order: 69
level: A
title: Plant Infection (multi-part)
quick: original-structured-preparation-guide · Plant Infection (multi-part)
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
      https://www.1point3acres.com/interview/problems/fca7001d-3089-4d7f-ae1f-5a44924f874d
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Plant Infection：多阶段题的稳健写法

> **已佐证内容**：本地原始面经明确记录：P1 中 `X` 每天感染周围 **8 个邻居**；P2 增加永不感染的 `I`；P3 感染 `D` 天后康复并转为免疫；P4 询问矩阵很大怎么办；P5 的具体题意未被记录。不能把其他资料里的死亡或 containment 规则硬塞成这个 UUID 的 P4/P5。

## 前三问

P1：`.` 为健康、`X` 为感染，每天同步扩散，直到 `newly_infected` 为空，返回稳定天数。P2：`I` 既不入队，也不能被覆盖。P3：把格子改成 `S / X(infected_day) / I` 状态机，并约定感染满 `D` 天后的事件顺序。

例如 `X.I.` 中，第一天第二格感染，第三格 `I` 阻断传播，第四格保持健康；若 `D=2`，初始 `X` 到约定的第 2 天转免疫。

## 可扩展算法骨架

每天严格分三步：读取旧状态收集传播候选；统一应用新感染；处理到期免疫事件。P1/P2 可用按层队列，P3 用 `recover_on[day] -> cells` 事件桶，避免每一天扫描全网格。

```text
new = collect_spread(old_active, old_grid)
apply_all(new)
apply_all(recover_on[t])
```



P4 的大矩阵若很稀疏，只保存非健康格、当前边界和到期事件；若数据在外存，则按 tile 分块并交换边界 halo。

## 复杂度与边界

单向状态转换时，时间 `O(RC·8)`、空间 `O(RC)`；稀疏版与实际活跃格和边界规模成正比。重点测试同步更新、`D=0/1`、全 `I`、无 `X`、免疫围墙，以及“当天到期者是否还能传播”。P5 必须看到原题再作答。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/fca7001d-3089-4d7f-ae1f-5a44924f874d)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
