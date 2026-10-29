---
id: drustz-7d4a25bf2accad592d
section: mlsd
order: 123
level: A
title: 16 · Case：设计 RL（post-training）数据流水线 · 20. 延伸阅读
quick: 作者文档章节 · 16 · Case：设计 RL（post-training）数据流水线 · 20. 延伸阅读
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
## 20. 延伸阅读

| 资料 | 分钟 | 用途 |
|---|---|---|
| [DAPO](https://arxiv.org/abs/2503.14476) | 25 | dynamic sampling 的出处，另外三个 trick（clip-higher / token-level loss / overlong reward shaping）在 §7.3、§10.1 都用到了 |
| [DeepSeekMath（GRPO 原始论文）](https://arxiv.org/abs/2402.03300) | 30 | 组内优势公式的出处，§7.1 的地基 |
| [DeepSeek-R1](https://arxiv.org/abs/2501.12948) | 40 | RLVR 的规模化叙事 + 语言混杂/可读性 reward 的工程妥协 |
| [Let's Verify Step by Step（PRM800K）](https://arxiv.org/abs/2305.20050) | 30 | 过程奖励 vs 结果奖励，对口 §10.1 |
| [Tülu 3](https://arxiv.org/abs/2411.15124) | 40 | 完整开源的 post-training 数据 recipe，含去污流程，是本篇最好的对照实现 |
| [Defining and Characterizing Reward Hacking（Skalse et al., NeurIPS 2022）](https://arxiv.org/abs/2209.13085) | 25 | §9.4 的理论背景：形式化「优化 proxy reward 反而降低真 reward」的条件 |
| [The Perils of Optimizing Learned Reward Functions](https://arxiv.org/abs/2406.15753) | 25 | 补充：reward model 的低训练误差**不**保证低 regret，对应「假阳性被主动搜索」 |
| **本地** [decagon_finetune L5 过程奖励](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/projects/decagon_finetune/levels/level5_process_reward/) | 15 | §10.1 那组 153 轨迹的实测数据 |
| **本地** [decagon_finetune L6 on-policy distillation](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/projects/decagon_finetune/levels/level6_onpolicy_distill/) | 20 | reverse KL 的可跑演示，追问时用 |
| **本地** [labs/lab02 reward 设计](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/labs/lab02_reward_design/) | 30 | hard gate → 可验证 outcome → quality → cost 的同一套结构 |
| **本地** [cs336 assignment5-alignment](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/cs336/assignment5-alignment/) | 90+ | post-training 的实操场；想把本篇变成 artifact 就跑它 |

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/16_case_rl_data_pipeline.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/16_case_rl_data_pipeline.md)。作者整理资料；许可和第三方来源范围见阅读指南。
