---
id: drustz-725dd7a810c25cdd7b
section: mlsd
order: 190
level: A
title: >-
  20 · Exa 第二轮技术面：agentic search 的 retrieval / reranking / snippet / alignment ·
  9. 45 分钟怎么走 ⭐
quick: >-
  作者文档章节 · 20 · Exa 第二轮技术面：agentic search 的 retrieval / reranking / snippet /
  alignment · 9. 45 分钟怎么走 ⭐
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/20_case_exa_agentic_search.md
    type: primary
---
## 9. 45 分钟怎么走 ⭐

| 时间 | 做什么 | 注意 |
|---|---|---|
| 0–3 | 自我介绍（[12 §2](?book=drustz-interview-2026&section=mlsd&question=drustz-9cf6cdf44534a561fb) 的 90 秒版，**换成 retrieval 口径**，见 §11） | 别背简历，只讲能接上今天题目的三条 |
| 3–6 | **澄清问题**（§3.1 那五个的对应版本） | 至少问 3 个。不问就开画 = 减分 |
| 6–9 | **写下优化目标和指标**，明确说"我先定成功的定义" | 这是 Exa 最看重的信号（他们整家公司都在讲 eval） |
| 9–16 | 画架构（v1 → v3 阶梯 + 升级触发条件） | **不要一上来就画最复杂的** |
| 16–24 | **算术**：延迟预算 / 算力 / 容量 | ⭐ 这是与其他候选人拉开差距的地方。白板上写 `2 × params × tokens` |
| 24–32 | 训练数据、负例、失败模式 | 主动说坑，不等他挖 |
| 32–38 | eval 与上线：baseline 阶梯、切片、护栏、降级打点 | |
| 38–43 | 收口：v1 交付什么、什么证据触发 v2 | "我会先上 bi-encoder + 预计算，量出离 oracle 的差距再决定要不要 cross-encoder" |
| 43–45 | 提问（见 §12） | |

### 90 秒开场（retrieval 口径改写版）

> 我最近的工作横跨 agentic LLM 的 post-training 和 retrieval。上一段在 Reflection 做 agent 系统；
> 最近自己搭了一套分级的 retrieval + post-training 实验台，从 eval baseline 一路做到 DPO / Dr. GRPO / on-policy distillation。
> 那套东西里我最大的收获其实是两个负结果：一个是**微调生成式 query rewriter 完全跨不了域，
> 但换检索器 + 微调 embedding 直接把 recall@5 从 0.165 拉到 0.576，一行训练代码都没写**；
> 另一个是我一开始报的 hard negative 收益，加了样本数对齐的对照组之后发现三分之二是假的，我把它划掉了。
> 所以我的习惯是：**先把 eval 和 baseline 立住，再动模型；每个收益都要有对照组**。
> 今天这题我会按这个顺序来。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/20_case_exa_agentic_search.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/20_case_exa_agentic_search.md)。作者整理资料；许可和第三方来源范围见阅读指南。
