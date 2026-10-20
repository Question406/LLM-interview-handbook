---
id: dt-reward-pref
section: panel
order: 5
level: S
title: Panel：奖励模型和偏好学习怎么选，坑在哪？
quick: "能执行验证的任务用规则奖励；主观偏好用人标，再选择 DPO 或带 RM 的在线 RLHF。AFM 用 RLOO，文本与图像文本走 RM，数学与视觉 STEM 走规则。RM 分数要与人评核对，偏好数据还要检查长度、礼貌和分歧等偏差。"
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
updatedAt: 2026-10-12
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
  - title: "Direct Preference Optimization: Your Language Model is Secretly a Reward Model"
    url: https://arxiv.org/abs/2305.18290
    type: primary
  - title: "ReMax / RLOO: Back to Basics"
    url: https://arxiv.org/abs/2402.14740
    type: primary
---

先看任务能否独立验证。代码测试、数学答案和工具状态可以用规则奖励；可读性等主观偏好才需要人标、奖励模型（RM）或 DPO。DPO 是利用偏好数据的方法，不能替代整个 RLHF 数据与验证流程；RM 也仍需人工校准。

不这么选的理由：guideline 写这支团队 alignment 和预训练都碰。人标偏好有 20-30% 分歧，AFM 用 cohesion 选 输入提示（prompt）。面试要能讲长度 hack 和过优化。现场只报 RM 分、不报 gold / 人评，就是在报 proxy。

## 先看信号能不能执行

| 信号 | 算法 | 为什么 |
| --- | --- | --- |
| 代码测试、数学答案、工具状态 | 基于可验证奖励的强化学习（RLVR） / 规则奖励 + 组采样（GRPO / RLOO） | oracle 可复现，RM 只会加噪声 |
| 已有干净偏好对、要离线、少采样 | DPO / IPO | 不需要在线 rollout，训练较稳定，但缺少在线探索 |
| 多目标、要在线探索、有可靠 RM | RLHF（PPO / RLOO） | 能混多个标量，成本高 |
| 人标分歧大、题很主观 | 先丢掉或降权，再训 RM | AFM：20-30% 偏好对上人本来就不同意 |

AFM 2025 的配方可以当现场例子。监督微调（SFT） 之后对端侧和 server 都做 RLHF，主算法是 RLOO。奖励两路走：文本和图像-文本用 RM（偏好损失 + 单边打分正则，和 2024 版一致）；数学和图像 STEM 用规则核验。全参数更新，视觉编码器也更新。异步基础设施把 trajectory generator 和 policy updater 拆开，公开数字是比同步系统少 37.5% 设备、少 75% 计算时间。报完数字要接一句：异步会引入 off-policy 程度，replay 不能无限陈旧。

RLOO 对同题采 $G$ 条回答，第 $i$ 条的 baseline 取其余 $G-1$ 条奖励的均值，因此不需要 value head。奖励相同，例如全对或全错时，相对 advantage 接近 0；与 GRPO 一样，需要处理没有相对学习信号的组。

## RM 和 DPO 各自 hack 什么

RM 过优化是老问题：策略把 RM 喜欢的表面特征推到极端，人评不动或掉。常见表面特征是长度、客套、列表、安全套话。InstructGPT 已经写过对齐会改能力剖面。现场要主动报 gold / 人评，不能只报 RM 分。

DPO 没有显式 RM，hack 改发生在数据上：标注者更爱长答案、只奖礼貌、offline 对和线上分布错位。$\beta$ 太大贴死 chosen，$\beta$ 太小几乎不更新。没有 RM 不等于更安全。

AFM 对文本 RM 还有一步公开的 prompt 选择：另训一个带 cohesion 头的 RM，看偏好标签是否和「总体有用性」互相推得出来，再在语义邻域里挑 cohesion 高的题。人本来就不同意的主观题，硬标只会把噪声写进奖励。他们报过这套选择带来 Arena Hard / AlpacaEval / Agent Sandbox / GPQA / Math500 和人评的增益。面试用这个当「数据比 loss 更值钱」的例子，不要背那一串百分数。

邮件摘要既要忠实又要好读，我会拆开收。忠实性可以核对陈述是否得到源文档支持，使用规则或证据支持奖励；好读是偏好，走人标 + RM。两路分数分开报，分开调权。合成「源里没有的细节」对抗题，奖拒答，见 `dt-synth-tool-mm`。若有人把用户邮件点赞当 RM 训练数据，在苹果默认不成立，见 `dt-privacy-feedback`。

长度：RM 或人评对长度做分层或归一，BoN 候选里留 SFT 样本，防止完全走到「又长又空」的角。

## 追问

- **为什么 AFM 用 RLOO 不用 PPO？** 公开理由没写「替代 PPO」。RLOO 省去价值评估模型（critic），适合最终给分、同一 prompt 可以多次采样的任务。需要逐步 credit 时 critic 仍有位置。
- **DPO 完还要不要 强化学习（RL）？** 格式和安全可以先离线 DPO；要探索新工具轨迹或新解法，还是要在线采样。AFM 的工具 hill-climb 写在 SFT 过程监督，RL 吃的是 RM + 规则。
- **人标 20-30% 不一致是不是数据坏了？** 对主观题这是预期。处理是选 cohesion 高的 prompt，不是逼标注员达成假一致。
