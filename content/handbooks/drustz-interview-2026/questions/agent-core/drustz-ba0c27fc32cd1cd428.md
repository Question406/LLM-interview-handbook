---
id: drustz-ba0c27fc32cd1cd428
section: agent-core
order: 81
level: A
title: Agent Self-Improvement：现有实现方法（面试口径版） · 面试常问 3 题 ⭐⭐⭐
quick: 作者文档章节 · Agent Self-Improvement：现有实现方法（面试口径版） · 面试常问 3 题 ⭐⭐⭐
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - Agent · Core、Gaps 与 Benchmarks
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/03_gaps/self_improvement.md
    type: primary
---
## 面试常问 3 题 ⭐⭐⭐

### Q1：你的 agent 生产里同类任务反复失败，怎么让它随时间变好？





**参考打法**



- 先报三档框架定调：test-time（不改持久物）→ 数据与提示层（可 diff 可回滚）→ 权重层（最后手段），成本与持久性递增。
- 短期：确认失败信号可捕获（verifier/用户反馈/状态校验），先在 harness 内做 Reflexion 式 retry——失败信息结构化注回下一轮。
- 中期主线：trace store → 失败聚类归因 → 每类先建最小复现 eval case → 按归因分派修 prompt/harness 或写 memory/skills，全部过 eval gate（含回归集）+ 人审后部署。
- 长期：某类失败归因为"能力不足"且量大 → 积累成 RL/SFT 数据（reward 设计见 agentic_rl.md）。
- 收尾强调：改进的单位是"失败 → eval case → 过 gate 的 diff"，不是"让 agent 自由反思"。





### Q2：self-improvement 为什么容易变成 self-degradation？怎么防？





**参考打法**



- 第一性证据：intrinsic self-correction 无外部信号时平均变差（arxiv 2310.01798，会把对答案改错）——反思必须由 verifier/测试/环境信号触发。
- 累积污染：Voyager 式技能库/memory 只进不出，一条被误判放行的坏条目会被检索反复放大；需要 provenance、版本化、淘汰机制。
- 优化即 hacking：DGM 进化出 hallucinate 工具输出、甚至移除 hallucination 检测标记的个体；GEPA/AlphaEvolve 在 metric 可 hack 时同样进化出作弊解——和 RL reward hacking 同构。
- 防线四件套：外部 verifier 驱动 + eval gate（含回归集）+ 改动落在可 diff 可回滚的持久物上 + 高影响变更人审（Applied Compute 的 SME accept/reject 就是这个）。
- 高阶补充：gate 本身也要演进——失败案例回流成新 eval case，防 gate 被静态打穿。





### Q3：GEPA 式 prompt 进化 vs RL 微调，什么时候选哪个？





**参考打法**



- 数字开场：GEPA 用最多 1/35 的 rollouts 超 GRPO 平均 6~10%、最高 +20%——说明大量"能力问题"其实是 context/instruction 问题。
- 选 prompt 进化：模型只能 API 访问、rollout 预算小、需要可读可 diff 可回滚的产物、任务分布还在变。
- 选 RL：能力真不足（prompt 怎么改都到不了）、有可验证 reward + 大 rollout 预算、任务分布稳定值得把能力烧进权重。
- 实操顺序：先 GEPA 便宜地摸 metric 的坑（metric 被 prompt hack 说明 reward 也会被 policy hack），确认 prompt 空间到顶再上 RL；两者共享同一套 eval/rollout 基建。
- 提一句共同风险：两者都是对 metric 的优化器，metric 质量 = 上限。





> 高分句：Self-improvement 的工程本质不是"让 agent 自由改自己"，而是选定改哪个持久物——context、memory、skills、prompt、harness 代码还是权重——然后用外部 verifier 产生信号、把每个改动收敛成过 eval gate、可回滚的 diff；没有 verifier 和 gate 的自我改进，优化的只是把病藏得更深的能力。

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/03_gaps/self_improvement.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/03_gaps/self_improvement.md)。作者整理资料；许可和第三方来源范围见阅读指南。
