---
id: drustz-b7bb43f4fc2b5e118e
section: agent-core
order: 47
level: A
title: Agentic RL（面试口径版） · 自学资料
quick: 作者文档章节 · Agentic RL（面试口径版） · 自学资料
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
## 自学资料

按优先级排序，标注读什么与预计时间：

1. [DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models](https://arxiv.org/abs/2402.03300) — GRPO 原始出处；只读 §4：目标函数推导、与 PPO 的关系、outcome vs process supervision · 30 min
2. [DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning](https://arxiv.org/abs/2501.12948) — 大规模 RLVR 实践：rule-based reward 设计、为何明确弃用 neural RM、R1-Zero→R1 的完整 pipeline · 40 min
3. [Tülu 3: Pushing Frontiers in Open Language Model Post-Training](https://arxiv.org/abs/2411.15124) — RLVR 命名出处；重点读 RLVR 章节的 verifier 构造与可验证 prompt 数据集 · 30 min
4. [From shortcuts to sabotage: natural emergent misalignment from reward hacking (Anthropic)](https://www.anthropic.com/research/emergent-misalignment-reward-hacking) — 生产 RL 环境 hack→misalignment 泛化 + inoculation prompting，Q2 最硬的实证弹药 · 25 min
5. [Detecting misbehavior in frontier reasoning models (OpenAI)](https://openai.com/index/chain-of-thought-monitoring/) — CoT monitoring 抓 hack 的方法与"优化 CoT 导致 obfuscation"负结果；配套论文 [arxiv 2503.11926](https://arxiv.org/abs/2503.11926) · 20 min
6. [TRL GRPOTrainer docs](https://huggingface.co/docs/trl/grpo_trainer) — GRPO 变体工程全景：loss_type 家族、scale_rewards、token vs sequence importance sampling，每个开关都注了出处论文 · 25 min
7. [Agentic RL: Token-In, Token-Out Done Right (HF blog)](https://huggingface.co/blog/huggingface/tito) — multi-turn 的 retokenization/loss mask 坑，为什么必须 token 进 token 出 · 20 min
8. [verl (GitHub)](https://github.com/volcengine/verl) — 生产级 RL 框架；读 README + multi-turn/agent loop 文档，理解 hybrid controller 与 rollout/train 共卡 · 30 min
9. [OpenRLHF (GitHub)](https://github.com/OpenRLHF/OpenRLHF) — Ray+vLLM 分离式架构与 REINFORCE++；对照 verl 看资源编排的另一种取舍 · 15 min
10. [Sycophancy to subterfuge: Investigating reward tampering (Anthropic)](https://www.anthropic.com/research/reward-tampering) — 早期实证：从sycophancy逐级泛化到篡改自己的 reward 函数 · 15 min

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/03_gaps/agentic_rl.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/03_gaps/agentic_rl.md)。作者整理资料；许可和第三方来源范围见阅读指南。
