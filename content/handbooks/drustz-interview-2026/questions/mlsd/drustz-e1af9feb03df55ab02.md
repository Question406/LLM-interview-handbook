---
id: drustz-e1af9feb03df55ab02
section: mlsd
order: 179
level: A
title: 19 · Case：设计 agent 能力 benchmark · 17. 延伸阅读
quick: 作者文档章节 · 19 · Case：设计 agent 能力 benchmark · 17. 延伸阅读
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/19_case_agent_benchmark.md
    type: primary
---
## 17. 延伸阅读

| 资料 | 分钟 | 用途 |
|---|---|---|
| [agentic2 · 04_benchmarks](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/agentic2/04_benchmarks.md) | 12 | 本篇的配套速查卡：主表、分数锚点、逐个 benchmark 的追问备答 |
| [τ-bench 论文](https://arxiv.org/abs/2406.12045) | 30 |  $\mathrm{pass}^k$  的出处；**失败分析章节**（对话分支敏感性）比主结果更值得读 |
| [Introducing SWE-bench Verified（OpenAI）](https://openai.com/index/introducing-swe-bench-verified/) | 15 | 三类坏题的分类学 + 人工筛题流程，本篇 §5.5 和 §6.1 的一手依据 |
| [SWE-bench Pro 论文](https://arxiv.org/abs/2509.16941) | 20 | 第 2–3 节：copyleft + held-out 商业集的三层防污染结构 |
| [OSWorld 官网与 Verified 榜](https://os-world.github.io/) | 10 | "评分脚本自己会坏"最好的公开证据 |
| [AgentDojo 论文](https://arxiv.org/abs/2406.13352) | 30 | utility + ASR 双指标；"攻防都是可编程组件"的框架设计 |
| [Terminal-Bench 2.0 leaderboard](https://www.tbench.ai/leaderboard/terminal-bench/2.0) | 5 | 每条 entry 标注 harness 且轨迹公开——"系统分不是模型分"的实例 |
| [DAPO](https://arxiv.org/abs/2503.14476) | 20 | dynamic sampling：本篇 §6.3 两阶段难度探测的理论对应 |
| 本地 [`projects/decagon_finetune/levels/level5_process_reward/`](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/projects/decagon_finetune/levels/level5_process_reward/) | 15 | §4.2 那张表的可执行版本，面试前跑一遍能把数字讲熟 |
| [08 · Evaluation 与成本闭环](?book=drustz-interview-2026&section=mlsd&question=drustz-f15a9e25a058981436) | 15 | judge calibration、slice 原则、发布阶梯——本篇不重复的通用部分 |

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/19_case_agent_benchmark.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/19_case_agent_benchmark.md)。作者整理资料；许可和第三方来源范围见阅读指南。
