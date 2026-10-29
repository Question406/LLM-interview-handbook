---
id: dt-reward-pref
section: panel
order: 5
level: S
title: Panel：reward model 和 preference learning 怎么选，坑在哪？
quick: >-
  先看任务能不能独立验证。代码测试、数学答案、工具状态用 rule-based reward，主观偏好才用人标，再选 DPO 或带 RM 的在线
  RLHF；AFM 用 RLOO，文本和图像-文本走 RM，数学和视觉 STEM 走规则。坑在过优化，RM 分要和 human evaluation
  核对，preference data 要查长度、礼貌和人与人分歧。
companies:
  - apple
tags:
  - Apple
  - Reward Model
  - Preference
  - RLHF
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: 'https://arxiv.org/abs/2203.02155'
    type: primary
  - title: >-
      Direct Preference Optimization: Your Language Model is Secretly a Reward
      Model
    url: 'https://arxiv.org/abs/2305.18290'
    type: primary
  - title: 'ReMax / RLOO: Back to Basics'
    url: 'https://arxiv.org/abs/2402.14740'
    type: primary
---

先看任务能不能独立验证。代码测试、数学答案和工具状态用 rule-based reward；可读性这类主观偏好才需要人标、reward model（RM）或 DPO。DPO 只是利用 preference data 的一种方法，RLHF 里的数据收集和验证流程照样要做，RM 也仍需人工 calibration。

举个例子，邮件摘要既要忠实又要好读，我会拆成两路。忠实性可以逐句核对陈述有没有源文档支持，用规则或证据支持奖励；好读是偏好，走人标加 RM。两路分数分开报，权重分开调。另外合成「源文里没有的细节」的对抗题，奖励拒答（`dt-synth-tool-mm`）。guideline 写明这支团队 alignment 和 pre-training 都会碰，所以面试要能讲清楚长度 hack 和过优化。

## 按信号选算法

| 信号 | 算法 | 为什么 |
| --- | --- | --- |
| 代码测试、数学答案、工具状态 | 基于 verifiable reward 的 RL（RLVR） / rule-based reward + 组 sampling（GRPO / RLOO） | oracle 可复现，RM 只会加噪声 |
| 已有干净 preference pairs、要离线、少 sampling | DPO / IPO | 不需要在线 rollout，训练较稳定，但缺少在线探索 |
| 多目标、要在线探索、有可靠 RM | RLHF（PPO / RLOO） | 能混多个标量，成本高 |
| 人标分歧大、题很主观 | 先丢掉或降权，再训 RM | AFM：20-30% preference pairs 上人本来就不同意 |

RLOO 对同一道题采 $G$ 条回答，第 $i$ 条的 baseline 取其余 $G-1$ 条奖励的均值，所以不需要 value head。如果奖励全都相同，比如全对或全错，相对 advantage 接近 0，和 GRPO 一样要处理这种没有相对学习信号的组。

AFM 2025 的 RLHF 主算法就是 RLOO，奖励按上表分两路：文本和图像-文本用 RM（偏好损失加单边打分正则），数学和图像 STEM 用规则核验。他们的异步基础设施把 trajectory generator 和 policy updater 拆开，公开数字是比同步系统少用 37.5% 的设备、少 75% 的计算时间。代价是异步会引入 off-policy 的程度，replay 不能无限陈旧。

## RM 和 DPO 各自会被 hack 在哪

RM 过优化是老问题：策略把 RM 喜欢的表面特征推到极端，human evaluation 却不动甚至下降，常见的是长度、客套、列表和安全套话。InstructGPT 就写过，对齐会改变模型的能力剖面。所以现场要主动报 gold 或 human evaluation 的结果，只报 RM 分，报的只是 proxy。

DPO 没有显式的 RM，hack 就转到了数据上：annotator 更爱长答案、只奖励礼貌、离线 preference pairs 和线上分布错位。$\beta$ 太大会贴死 chosen，$\beta$ 太小几乎不更新。没有 RM 不等于更安全。针对长度，RM 或 human evaluation 要对长度做分层或归一，BoN 候选里保留 SFT 样本，防止策略走到「又长又空」的角落。

## 追问

**preference data 怎么挑题？**
先把人本来就不同意的主观题挑出去，硬标只会把噪声写进奖励。AFM 另训了一个带 cohesion 头的 RM，看 preference labels 和「总体有用性」能不能互相推出，再在语义邻域里挑 cohesion 高的 prompt。他们报过这套选择在 Arena Hard、AlpacaEval、Agent Sandbox、GPQA、Math500 和 human evaluation 上都有增益。面试里拿它说明挑数据比改 loss 更值钱，那一串百分数不用背。

**为什么用 RLOO 不用 PPO？**
公开报告没写「替代 PPO」的理由。RLOO 省掉了价值评估模型（critic），适合最终才给分、同一个 prompt 可以多次 sampling 的任务。需要逐步分配 credit 时，critic 仍有用武之地。

**做完 DPO 还要不要 RL？**
格式和安全可以先用离线 DPO；要探索新的 tool-use trajectories 或新解法，还是要在线 sampling。AFM 的工具 hill-climb 写在 SFT 的过程监督里，RL 用的是 RM 加规则。

**人标有 20-30% 不一致，是不是数据坏了？**
对主观题，这在预期之内。处理方法是挑 cohesion 高的 prompt，让 annotator 各自独立判断，别逼出虚假的一致。

**能拿用户对邮件的点赞来训 RM 吗？**
要先过许可和隐私这一关，见 `dt-privacy-feedback`。
