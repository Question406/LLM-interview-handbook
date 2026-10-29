---
id: drustz-e3cf9b62cf476975f7
section: agent-core
order: 42
level: A
title: Agentic RL（面试口径版） · 30 秒版本（3 句话）⭐⭐⭐
quick: 作者文档章节 · Agentic RL（面试口径版） · 30 秒版本（3 句话）⭐⭐⭐
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/03_gaps/agentic_rl.md
    type: primary
---
## 30 秒版本（3 句话）⭐⭐⭐

1. Agentic RL = 在真实/仿真环境里采 multi-turn tool-use rollout，用可验证的终局信号（测试通过、任务完成）做 reward 来 post-train agent policy——2024 起主线从 RLHF 的偏好对齐转向 RLVR 的任务能力。
2. 核心工程事实：**training harness 就是 eval harness 加一个 reward 出口**——env、sandbox、tool executor、trace 采集、grader 全部复用，区别只是 grader 输出从 pass/fail 变成 reward 标量回流 trainer（harness 侧见 [03_harness_env_swe.md](?book=drustz-interview-2026&section=agent-core&question=drustz-313f5f3c3ba19b2ed7)）。
3. 主流算法是 GRPO：同一 prompt 采一组 rollout，用组内相对 reward 当 advantage，砍掉 PPO 的 value network——对 reward 稀疏、序列超长的 agent 任务工程上更省。

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/03_gaps/agentic_rl.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/03_gaps/agentic_rl.md)。作者整理资料；许可和第三方来源范围见阅读指南。
