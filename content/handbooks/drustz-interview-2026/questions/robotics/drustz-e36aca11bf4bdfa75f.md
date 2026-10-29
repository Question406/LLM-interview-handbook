---
id: drustz-e36aca11bf4bdfa75f
section: robotics
order: 16
level: A
title: '02 — 轮次形式与情报（The Bot Company Onsite, 13:00–17:00） · 4. 类比公司面经中可复用的具体题目'
quick: >-
  作者文档章节 · 02 — 轮次形式与情报（The Bot Company Onsite, 13:00–17:00） · 4.
  类比公司面经中可复用的具体题目
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - Robotics · Data、Learning 与 System Design
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/02_interview_rounds_intel.md
    type: primary
---
## 4. 类比公司面经中可复用的具体题目

这些是**真实出现过的题**（来源标注），风格与 The Bot Company 面试官母体高度重合，直接拿来练：

| # | 题目 | 来源 | 练法 / 答题要点 |
|---|---|---|---|
| 1 | "10,000 小时 teleoperation 数据 + 100 小时真机 rollout，怎么合起来训一个 policy?" | Skild AI problem session | 核心张力：teleop 量大但 off-policy/分布偏、rollout 量小但 on-policy。答：先 BC on teleop 打底 → rollout 做 RL fine-tune 或 filtered BC（只学成功轨迹）→ 关键是 rollout 数据加权/重放策略 + 用 rollout 分布做 eval 集。**这题就是 LLM 的 SFT→RLHF 结构，明说这个映射** |
| 2 | "BC 为什么会 compounding errors，DAgger 修了什么、没修什么?" | Skild AI | 答：BC 只见过 expert 状态分布，policy 一步偏离就进入没见过的状态 → 误差随 horizon 累积（quadratic in T vs. DAgger 的 linear）。DAgger 修了 distribution shift（在 policy 自己的状态上收 expert 标注），没修：expert 本身不可达/次优、标注成本、多模态动作分布的模式平均问题 |
| 3 | "quadruped 上没见过的冰面，sim-to-real 哪里先崩?" | Skild AI | 答摩擦系数在训练时的 randomization 范围外 → 接触动力学首先崩。被追问时给具体参数：randomize 了 friction coefficient 什么范围、质量/电机延迟/地形怎么随机化。**这题的元教训：说 domain randomization 必须能报出参数和范围，否则 "hand-wave and you're done"** |
| 4 | 手写 attention / transformer 模块 | Tesla 电面高频（1p3a/Blind） | 默写到 5 分钟内无 bug，含 causal mask + padding mask 变体，shape 注释齐全 |
| 5 | Importance sampling 实现/推导 | Tesla 电面（1p3a） | 能写估计量、说明高方差问题和 clipping；顺手连到 PPO ratio clipping——面试官是 RL at scale 背景 |
| 6 | Circular array / 环形缓冲实现 | Tesla 电面（1p3a） | 15 分钟内写完带测试；机器人语境 = 传感器流缓冲，可主动点破这个联系 |
| 7 | 单遍 reverse 迭代算 discounted returns（向量化） | Skild coding 轮 | `G[t] = r[t] + γ·G[t+1]`，先写 reverse 循环版，再讨论能否向量化（`scipy.signal.lfilter` 或 log-space 前缀技巧），并处理 episode boundary mask |
| 8 | 对简历 ML 项目的技术难点连环追问（电面前 15–20 分钟就开始） | Cruise MLE 流程 | 用 3.1 的四段式；准备好被打断和跳问 |
| 9 | 开放式 CV/ML 设计题 + 基础知识混考（有人挂在这轮） | Figure AI 1p3a | 弱区自查：经典 CV/ML 基础（BN vs LN 为什么、优化器差异、为什么 policy 输出用 diffusion/action chunking——至少能讲一手原理） |
| 10 | "讲你自己的工作并接受盘问"（project talk 独立成轮） | Skild AI | 等同情景 C 的 presentation 轮，练一个 15 分钟无 slides 口头版 |

**练习优先级（时间只够练一半时）：** #1、#2（开放推理，直接对口他们的业务）→ #4、#7（coding 最可能形态）→ #3（sim2real 是 CTO 点名词）→ 其余。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/bot_company/02_interview_rounds_intel.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/02_interview_rounds_intel.md)。作者整理资料；许可和第三方来源范围见阅读指南。
