---
id: drustz-ac4e830396cfc7a740
section: mlsd
order: 127
level: A
title: 17 · Case：设计合成数据生成系统 · 1. 先问清楚：合成数据是五个任务 ⭐⭐⭐
quick: 作者文档章节 · 17 · Case：设计合成数据生成系统 · 1. 先问清楚：合成数据是五个任务 ⭐⭐⭐
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - ML System Design · 全流程
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/17_case_synthetic_data.md
    type: primary
---
## 1. 先问清楚：合成数据是五个任务 ⭐⭐⭐

### 1.1 七个澄清问题（每个都改变设计）

| # | 问题 | 答案会改变什么 |
|---|---|---|
| 1 | **目的是哪一个？**（总量 / 长尾 / 隐私 / 标注成本 / 难度控制） | 决定"是否需要匹配真实分布"这一条根本约束，见 §1.2。答错这题后面全错 |
| 2 | **有没有 verifier？**（可执行、可判定、可对答案） | 有 verifier → 生成可以放开、筛选可以自动、reward 可以硬。没有 → 全部退化为 judge + 人评，成本高一个量级，见 §4 |
| 3 | **数据用在哪一段训练？**（CPT / SFT / preference / RL / eval） | RL 要的是**难度落在梯度区间**的题（§5）；SFT 要的是**正确且风格一致**的示范；eval 要的是**绝不能被训练见过**的样本。同一批数据不能三用 |
| 4 | **teacher 从哪来、许可如何？** | 用商业 API 的输出训自己的模型，很多服务条款是禁止的；用开源权重模型（Nemotron-4 340B 就明确以宽松许可发布、鼓励用于合成数据）则没这个问题。这是**法务约束不是技术约束**，但面试里主动提会加分 |
| 5 | **种子数据（seed）有多少、有多脏？** | 多样性的上限来自 seed，不来自 prompt（§6.2）。只有 200 条 seed 就想造 50 万条多样样本，答案是"造不出来，先去扩 seed" |
| 6 | **真实数据的边际成本是多少？** | 如果标一条真实数据 &#36;0.5，合成 + 筛选一条 &#36;0.4 且质量更差，那这个项目就不该做（§10） |
| 7 | **迭代节奏与代际？**（一次性交付 / 每周再生成 / 用自己训出的模型再生成） | 决定要不要建代际治理（§7）。一次性生成不会坍塌；连续三代自产自销会 |

补充两个"如果时间够就问"的：**目标语言/领域的分布**（低资源语言的 generator 本身就弱）、**能否接触真实用户数据**（决定 §9 隐私路径）。

### 1.2 五种目的 → 五套设计（这张表是本题的骨架）

| 目的 | 是否要匹配真实分布 | 主评估 | 主要风险 | 合适范式 |
|---|---|---|---|---|
| **总量不足**（token 不够） | 大致匹配 | 下游 loss / 能力 benchmark，matched-compute | 信息密度低、复读、坍塌 | 真实文本改写（rephrase / backtranslation）、教科书式生成 |
| **长尾覆盖** | **故意不匹配**（就是要oversampling稀有格） | 目标 slice 上的错误率下降，且头部不退化 | 生成的"长尾"是想象出来的，不是真实长尾 | 模板 + 组合枚举、从真实错误案例反推、evol-instruct 加约束 |
| **隐私替代** | **必须严格匹配** | TSTR（train-on-synthetic, test-on-real）对比 TRTR；同时测泄漏 | 泄漏原文；或为了隐私把分布抹平到没用 | DP 训练的 generator + sampling；结构化数据的条件生成 |
| **标注成本** | 匹配输入分布，标签要准 | 与人标金标的一致率 + 下游提升 | teacher 的系统性错误被固化 | distillation、rejection sampling、weak supervision 组合 |
| **难度控制**（RL/curriculum） | 无所谓分布，只在乎**可解率落区间** | RL 训练的梯度信号占比、上分速度 | 全对/全错的题占满 batch，白烧算力 | verifier + 在线可解率探测（§5） |

**高分句**：这五个目的对"和真实分布的差距"要求是相反的。补长尾时我**要**分布偏移——那正是我付钱买的东西；做隐私替代时同样的偏移就是缺陷。所以我不会一上来报一个"分布相似度"指标，我会先问目的，再决定这个指标是往 0 优化还是往目标 slice 上定向放大。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/17_case_synthetic_data.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/17_case_synthetic_data.md)。作者整理资料；许可和第三方来源范围见阅读指南。
