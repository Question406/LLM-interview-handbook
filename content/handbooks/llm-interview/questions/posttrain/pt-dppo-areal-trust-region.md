---
id: pt-dppo-areal-trust-region
section: posttrain
order: 251
level: S
title: TRPO、DPPO、AReaL 各自怎么给 RL 目标加 trust region？
quick: >-
  TRPO 对整份分布的 KL 加硬约束，要二阶计算；DPPO（Divergence PPO）用估出来的 TV / KL 代替单点 $\rho$ 来 mask
  更新；AReaL 约束的是样本年龄，过旧的轨迹过滤或降权。PPO 的 clip 只是拿一个 sampling token 的比率粗估分布变化。
tags:
  - TRPO
  - DPPO
  - AReaL
  - Trust Region
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: Trust Region Policy Optimization
    url: 'https://arxiv.org/abs/1502.05477'
    type: primary
  - title: Rethinking the Trust Region in LLM Reinforcement Learning
    url: 'https://arxiv.org/abs/2602.04879'
    type: primary
  - title: AReaL
    url: 'https://arxiv.org/abs/2505.24298'
    type: primary
---

三者约束的东西不一样。TRPO 对整份条件分布的 KL 加硬约束，要做二阶计算；DPPO 先估出 TV 或 KL，再用它来 mask 更新，替掉 PPO 那个单点的 $\rho$；AReaL 约束的是样本有多旧，版本差太大的轨迹过滤掉或者降权。两套 KL 的 reference policy 怎么分见 `pt-trust-region-vs-drift-kl`，这张卡讲近端约束怎么落地：硬 KL、ratio clip、散度 mask，还是异步样本的年龄。

名字先对齐。2026 社区 35 题里的 DPPO，默认指 Divergence Proximal Policy Optimization（`2602.04879`），和 Distributed PPO、以及把 IS 和 clip 拆开的 Decoupled PPO 都不是一个东西。名字撞了先问对方指哪个。

## TRPO：约束写在分布上

$$
\max_\theta\ L_{\pi_{\mathrm{old}}}(\pi_\theta)\quad\text{s.t.}\quad
\mathbb{E}_s\big[D_{\mathrm{KL}}(\pi_{\mathrm{old}}(\cdot\mid s)\,\|\,\pi_\theta(\cdot\mid s))\big]\le\delta.
$$

它约束的是**整份条件分布**的 KL，跟某一个被 sampling token 的 $\rho$ 无关。实现要走 Fisher 矩阵和共轭梯度，大 vocabulary 的 LLM 基本不用。PPO 用 $\mathrm{clip}(\rho,1-\varepsilon,1+\varepsilon)$ 做一阶的工程近似，见 `pt-ppo-clip`。

这个近似在 LLM 上会歪。$|\rho-1|\le\varepsilon$ 相当于拿一个被 sampling token 的比率去估总变差。低频的探索 token，$\rho$ 噪声大，容易被 clip 掉，CISPO 和 clip-higher 想救的就是这类 token，见 `pt-cispo`、`pt-dapo`。高频 token 的 $\rho$ 接近 1，分布其实可能已经漂得很远，clip 照样放行。比如某个位置上高频词的概率几乎没变，剩下那部分概率质量却已经在其他词之间大幅挪动。所以 clip 并没有真的算 KL，它只是一个很吵的 Monte Carlo 估计。

## DPPO：直接估散度再 mask

Divergence PPO 还是用 policy gradient 的 surrogate，只是判断进出信任域时，用 TV 或 KL 的估计代替 $|\rho-1|$。vocabulary 太大，精确散度太吃显存，论文用了两种近似：**Binary**，把概率分成「被 sampling 的 token」和「其余 token」两部分；以及 **Top-$K$**。mask 是非对称的，只挡「已经在往 out-of-domain 走」的更新，把 $\rho$ 往 1 拉回来的步不挡。VeRL 文档里有 Binary-TV / Binary-KL 的实现。

实现时 trust region 要锚在**行为策略，也就是引擎实际 sampling 的分布** $\mu$ 上，别锚在训练图重算出来的 $\pi_{\mathrm{old}}$ 上。没有信任域的 CISPO 或纯 IS，训练和推理分布的差异会一步步累积，训练就不稳。drift KL 相对的是冻结的 $\pi_{\mathrm{ref}}$，那是另一回事，别和 DPPO 的一步约束合成一个 $\beta$。

## AReaL：约束样本有多旧

AReaL 要解决的是同步 RL 得等最慢的轨迹、生成和训练没法同时跑的问题，见 `sys-areal-vs-slime`。改成 fully async 以后，一个 batch 里会混着好几个 policy 版本的样本。它的「trust region」是 **staleness-aware** 的：版本差太大的轨迹丢掉或降权，打断生成时 flush 掉 KV，见 `sys-partial-kv-policy`、`sys-staleness`。它改的是数据准入，没有把 $\rho$ 换成 TV。

四种放在一起对照：

| | 约束对象 | 典型实现 |
| --- | --- | --- |
| TRPO | 分布 KL | 二阶、硬 $\delta$ |
| PPO / GRPO | 单点 $\rho$ | clip |
| DPPO | 估出来的 TV / KL | 动态 mask |
| AReaL | 样本年龄 / 版本 | 过滤、加权、打断续写 |

## 追问

**DPPO 和 CISPO，谁还留着信任域？**
DPPO 留着。CISPO 越界后仍回传 $\nabla\log\pi$，等于放弃了近端约束，DPPO 认为这正是 mismatch 累积的原因。一个救的是低频 token 的梯度，一个救的是分布约束。

**学习率已经很低了，还要信任域吗？**
DPPO 论文的结论是要。学习率低到 $10^{-6}$，也挡不住训练和推理的数值差异在多步更新里累积。

**Distributed PPO 怎么讲？**
那是系统层面的东西，sampling 和更新并行跑，放在框架题里讲，见 `sys-llm-rl-framework-index`。别和 Divergence PPO 抢缩写。
