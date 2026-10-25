---
id: pt-rl-checkpoint-selection
section: posttrain
order: 231
level: S
title: RL 训练过程中如何选 checkpoint（不是 Agent 状态存档）？
quick: "用开训前写死的多目标规则，在冻结的 held-out 任务、安全回归集和长度 / KL 约束上一起选，通常取验证集上 Pareto 可接受的较早稳定点。训练 proxy reward 的峰值和最后一步都不可靠，选点集本身也会因为看得太多而过拟合。"
tags:
  - RLHF
  - Checkpoint
  - Evaluation
  - Overoptimization
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Scaling Laws for Reward Model Overoptimization
    url: https://arxiv.org/abs/2210.10760
    type: primary
---

我会在开训前写好一条选点规则，用冻结的 held-out 任务、安全回归集和长度 / KL 约束一起卡，最后通常落在验证集上一个较早的稳定点。训练曲线上 proxy 奖励分数（reward）的峰值和「最后一步」都不可靠。这里的 checkpoint 指训练轨迹上的参数快照 $\theta_t$，和 Agent 环境的 state 存档是两回事，后者见 `arl-checkpoint`（逻辑状态、工具句柄、文件系统快照）。

为什么不能看峰值。Gao 等的 overoptimization 曲线已经说明，对训练用的奖励模型（RM）优化越久，gold 或人类分常常先升后降，最高的训练奖励往往对应过度优化，真实任务和安全可能已经回退了。比如数学强化学习（RL）里，step 2k 验证准确率最高，到 4k 时 training RM 分更高，但代码集和拒答集掉点，这时应该选 2k（或 2k-3k 的 EMA），别选最新一步。「最后一步」的习惯来自监督微调（SFT）：交叉熵损失（CE）还在降就接着训；可 RL 的 proxy 在 gold 掉头之后还能继续涨。

规则里至少同时盯三类指标。主能力，比如 held-out pass@k 和 arena 切片，评测包和训练隔离；安全和拒答，和 `pt-safety-capability-regression` 用同一套双门禁，切片不加权；代价，包括平均和 P95 token 用量、相对 $\pi_{\mathrm{ref}}$ 的 KL、工具成功率。规则要写成能执行的谓词，例如「安全违反 $\le$ 基线 $+0.5\%$，且主指标不低于峰值的 $98\%$，取最早满足的稳定窗」，别靠开会看曲线手选。这三维也别事后加权成一个「综合分」再 $\mathrm{argmax}$，那就偷换成了 `pt-multi-objective-reward-pareto` 里已经否定的标量化。安全和长度是硬约束，能力是约束内的最大化，画的是验证集上的 Pareto。

裁判要独立。同一个 RM 既当训练奖励又当选点依据，等于没有裁判，要用独立 judge、可执行 oracle 或冻结的人标集。`data-offline-online-metric-gap` 在这里同样成立：离线 win-rate 的峰值不一定对应线上效用，更不能让训练 RM 给自己发奖。单点峰值可能只是运气，可以用滑动窗口稳定性代替，比如连续 $N$ 次评估没有显著恶化。

评估本身也有讲究。评估频率是个超参，太密会在噪声上选点、泄漏测试信号，太疏会错过崩点。常见做法是按 token 或 step 固定间隔在 validation 上打点，最终测试包只碰一次。验证集也会被选点过拟合：每多看一次曲线、多调一次阈值，都要在报告里记一笔 peek，并保留一个从没用于选点的终测包。存储预算只够留少数快照时，按验证门禁存，等间隔存不划算；崩点附近加密，前期平台期可以稀一点。

如果后期只有 proxy 在涨，gold 不动或者安全掉了，就早停或回滚，别加步数「再冲一冲」。这和 `pt-reward-ood-failure` 是同一个信号：proxy-gold 的相关性掉下来，比「训练 reward 还在涨」更早出现。选中的 $\theta_t$ 最好再用影子流量或小流量 A/B 确认一次，held-out 仍可能和线上意图不一致。对外报告写清选点规则和偷看次数，让人能复现「为什么是这一步」：靠的是多目标门禁，训练曲线上的 $\mathrm{argmax}_t$ 说明不了。

## 追问

**和 `arl-checkpoint` 什么关系？**
没关系。这题是训练轨迹上的 $\theta_t$，`arl-checkpoint` 是恢复 Agent 逻辑状态和外部环境句柄，一个存 $\theta$，一个存 Agent 的世界状态。面试里先把对象划清，两个词别混用。

**能不能用训练 RM 选点？**
不能当唯一依据。它和优化目标是一伙的，会把 overoptimization 当成进步。

**评估偷看怎么办？**
留一个完全冻结的最终测试包，选点只用 validation，并报告 peek 次数。选点集调过太多次，等于又做了一次过拟合。

**用 EMA 还是单点？**
指标抖的时候用邻近步的 EMA 或滑动窗口；安全违反这种硬约束仍按最差窗口卡死，不能被平均掉。
