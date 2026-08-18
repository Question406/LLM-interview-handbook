---
id: pt-best-of-n-decomposition
section: posttrain
order: 29
level: S
title: Best-of-N 的提升中，生成器覆盖率与 Verifier / Selector 排序能力各贡献多少？如何分配算力？
quick: 把 Best-of-N 拆成“候选池有没有正确答案”和“selector 能否挑中它”。先报告 oracle-selection 上界，再报告 selector gap；若覆盖率低就增加或改善生成，若 gap 大就投资 verifier，而不是盲目增大 N。
tags:
  - Best-of-N
  - Verifier
  - Evaluation
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: OpenAI — Solving Math Word Problems
    url: https://openai.com/index/solving-math-word-problems/
    type: primary
---

对每个题目保留全部 `N` 条候选，并用可靠 oracle 标记候选正确性。candidate coverage 是候选池至少包含一个正确答案的比例；oracle selection 是假设完美 selector 时的上界；实际 Best-of-N 与上界的差就是 selector/verification 的空间。

画出 N–coverage、N–oracle、N–actual 三条曲线。若 N 增大后 coverage 已饱和而 actual 不涨，通常是候选高度相关、verifier 校准差或 selector 偏好冗长答案；若 actual 接近 oracle，则继续改善生成分布更有价值。

比较时要把生成、judge、重试、聚合的 token 和延迟全部计入。只报最终 BoN 分数会掩盖“模型变强”与“测试时多花算力”的区别。
