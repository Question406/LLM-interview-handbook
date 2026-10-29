---
id: drustz-b30f77f69f8ae141af
section: mlsd
order: 106
level: A
title: 16 · Case：设计 RL（post-training）数据流水线 · 3. 先问清楚：八个澄清问题 ⭐⭐⭐
quick: 作者文档章节 · 16 · Case：设计 RL（post-training）数据流水线 · 3. 先问清楚：八个澄清问题 ⭐⭐⭐
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/16_case_rl_data_pipeline.md
    type: primary
---
## 3. 先问清楚：八个澄清问题 ⭐⭐⭐

每个问题后面那一列是关键——面试官要看的是你知道**这个答案会改变什么**。

| # | 问题 | 答案会改变什么设计决策 |
|---|---|---|
| 1 | **训哪个模型、从哪个 checkpoint 起？基座是已经 SFT 过的还是裸的？** | 决定整个难度分布。同一批题对 8B 全错、对 200B 全对。**如果基座连格式都不稳，RL 之前先补 SFT，这条 pipeline 的第一版就白做**（RL 放大已有能力，不凭空创造） |
| 2 | **RL 算法是什么？GRPO 类（组内normalization）还是带 critic 的 PPO？组大小 G 多少？** | GRPO 类下全对/全错**严格贡献 0 梯度**，难度筛选是刚需；带 value critic 的 PPO 仍能从全对组里得到一点信号（value 基线不等于组均值），筛选可以宽松些。G 决定退化概率（§7.1 的表） |
| 3 | **目标能力是什么？单域（math）还是多域混合（math + code + agentic + 通用推理）？** | 决定要不要做跨域难度normalization、配比方法（§11）、以及 verifier 栈的复杂度。**多域是完全不同的一道题**——单域的 pipeline 可以两周做出来，多域主要成本在跨域可比性 |
| 4 | **终态可以程序化检查吗？可验证的比例大概多少？** | 这是可行性边界。如果 <30% 可验证，先做的不是 pipeline 是**可验证化**（§6）；如果基本不可验证，那这题应该退回 preference/rubric 路线，见 [03 §5](?book=drustz-interview-2026&section=mlsd&question=drustz-c7127e4b503f4848b2) |
| 5 | **compute 预算怎么切：数据生成 vs 训练？两者是同一批 GPU 吗？** | 关键约束。**筛选就是 rollout，和训练抢同一批卡**。如果是同一个池子，筛选的 12% 是从训练预算里扣的，要能论证这笔账（§7.2 的成本账） |
| 6 | **有没有真实使用场景的 prompt 分布？** | 决定合成的目标分布。没有的话，合成会不自觉地收敛到「教科书题」，训出来的模型在真实分布上不涨 |
| 7 | **eval 集是哪些？锁定了吗？还会加吗？** | 决定去污范围。**eval 没锁定就要按最坏情况去污**（把整个来源域拉黑而不是只删命中项）。另外要问 eval 是不是也用来做 early stopping——如果是，它已经不是 held-out 了 |
| 8 | **迭代节奏：数据是一次性交付，还是每周/每天出一版跟着训练走？** | 决定架构。一次性 = 批处理脚本；跟着训练走 = 需要增量化、缓存、幂等、和训练器的 checkpoint 同步（§13）。**RL 数据 pipeline 通常是后者，因为难度会漂移** |

> **可选第 9 问**（有安全/合规上下文时问）：有没有必须 hard-gate 的行为？如果有，它不能进 reward 的加权项，必须是独立的一票否决（[03 §6](?book=drustz-interview-2026&section=mlsd&question=drustz-c7127e4b503f4848b2)）。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/16_case_rl_data_pipeline.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/16_case_rl_data_pipeline.md)。作者整理资料；许可和第三方来源范围见阅读指南。
