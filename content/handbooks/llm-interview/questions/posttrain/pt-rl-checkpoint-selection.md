---
id: pt-rl-checkpoint-selection
section: posttrain
order: 231
level: S
title: RL 训练过程中如何选 checkpoint（不是 Agent 状态存档）？
quick: >-
  不要只看训练 proxy reward 峰值或最后一步。用冻结的 held-out 任务、安全回归集与长度/KL 约束做多目标选择，
  并警惕在评估器上过拟合；常取验证集上 Pareto 可接受的较早稳定点。
tags:
  - RLHF
  - Checkpoint
  - Evaluation
  - Overoptimization
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: Scaling Laws for Reward Model Overoptimization
    url: https://arxiv.org/abs/2210.10760
    type: primary
---

面试陷阱是把训练曲线上的 proxy reward 峰值，或「最后一步」，当成最好的模型。这里的 checkpoint 指训练轨迹上的参数快照 $\theta_t$，**不是** Agent 环境的 state 存档——后者见 `arl-checkpoint`（逻辑状态、工具句柄、文件系统快照）。Gao 等的 overoptimization 曲线已经说明：对训练 RM 优化越久，gold / 人类分常常先升后降。最高训练奖励往往对应对代理奖励的过优化，真实任务与安全可能已回退。

## 选点协议必须预先冻结

选择规则要在开训前写死，避免对着评估器反复 peek。至少同时盯：

- 主能力：held-out pass@k、arena 切片，评测包与训练隔离；
- 安全 / 拒答：和 `pt-safety-capability-regression` 同一套双门禁，切片不加权；
- 代价：平均 / P95 token、相对 $\pi_{\mathrm{ref}}$ 的 KL、工具成功率。

同一 RM 既当训练奖励又当选点依据，等于没有独立裁判。应使用独立 judge、可执行 oracle 或冻结人标集。`data-offline-online-metric-gap` 在这里同样成立：离线 win-rate 峰值不必对应线上效用，更不能用训练 RM 自己给自己发奖。可用滑动窗口稳定性（连续 $N$ 次评估无显著恶化）代替单点运气峰值。评估频率也是超参：太密会在噪声上选点并泄漏测试信号，太疏会错过崩点。常见做法是按 token / step 固定间隔在 validation 上打点，最终测试包只碰一次。选点规则要写成可执行的谓词，例如「安全违反 $\le$ 基线 $+0.5\%$，且主指标不低于峰值的 $98\%$，取最早满足的稳定窗」，而不是开会看曲线手选。能力、安全、成本三维不要事后加权合成一个「综合分」再 $\mathrm{argmax}$——那会把本题偷换成 `pt-multi-objective-reward-pareto` 里已经否定的标量化。验证集本身也会被选点过拟合：每多看一次曲线、每多调一次阈值，就要在报告里记一笔 peek，并保留从未用于选点的终测包。

## 后期只涨 proxy 就该早停

数学 RL 常见：step 2k 验证准确率最高，4k 时 training RM 更高但代码集与拒答集掉点——应选 2k（或 2k–3k 的 EMA），而不是最新一步。「最后一步神话」来自 SFT 的习惯：CE 还在降就继续；RL 的 proxy 可以在 gold 已经掉头之后继续涨。对外报告写清选点规则与偷看次数；多次在同一选点集上调阈值，本身就是元过拟合。若后期只有 proxy 涨、gold 不动或安全掉，应早停或回滚，而不是加大步数「再冲一冲」。这和 `pt-reward-ood-failure` 同一信号：proxy–gold 相关掉了，比「训练 reward 还在涨」更早。多目标选点画的是验证集 Pareto，不是训练曲线的最高点：安全与长度是硬约束，能力是约束内最大化。和 `arl-checkpoint` 的对比一句话就够：一个存的是 $\theta$，一个存的是 Agent 世界状态，不要把两个词混用。若计算预算只允许存少数快照，优先按验证门禁存，而不是按等间隔存；崩点附近加密采样，前期平台期可以更疏。选中的 $\theta_t$ 还要用影子流量或小流量 A/B 再确认一次，因为 held-out 仍可能和线上意图不一致，见 `data-offline-online-metric-gap`。

面试收口：checkpoint 选择是多目标门禁，不是 $\mathrm{argmax}_t$ 训练曲线。协议写在开训前，报告里能复现「为什么是这一步」。

## 追问

- **和 `arl-checkpoint` 什么关系？** 无关。本题是训练轨迹上的 $\theta_t$；`arl-checkpoint` 是恢复 Agent 逻辑状态与外部环境句柄。面试里先划清对象。
- **能不能用训练 RM 选点？** 不能当唯一依据。它与优化目标共谋，会把 overoptimization 当成进步。
- **评估偷看怎么办？** 预留完全冻结的最终测试包，选点只用 validation；报告 peek 次数。选点集调过太多次，等于又做了一次过拟合。
- **EMA 还是单点？** 指标抖时用邻近步 EMA 或滑动窗口；硬约束（安全违反）仍按最差窗口卡死，不能被平均掉。
