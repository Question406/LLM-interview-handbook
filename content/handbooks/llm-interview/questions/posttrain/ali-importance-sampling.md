---
id: ali-importance-sampling
section: posttrain
order: 5
level: A
title: GRPO/PPO 为何需要 importance sampling？新旧策略差很大时还有用吗？
quick: >-
  需要。实际训练用旧策略采的轨迹更新新策略好几步，要用 $\rho$ 把贡献校正回当前策略。新旧策略差太大时，$\rho$ 方差爆炸、clip
  频繁触发，估计质量变差，应更频繁地同步 sampling 策略或缩小更新。
tags:
  - Alibaba
  - GRPO
  - PPO
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: ↗ 阿里国际大模型算法一面
    url: 'https://www.nowcoder.com/feed/main/detail/27a27fc44b8a4613ae790ba27add8850'
    type: legacy-reference
---

需要，因为工程上几乎总是近似 on-policy：用 $\pi_{\mathrm{old}}$ 采一批 sampling 轨迹（rollout），再用 $\pi_\theta$ 在上面更新好几个 epoch，重要性比把这些数据的贡献校正回当前策略。新旧策略差很大时，$\rho$ 方差爆炸、clip 频繁触发，估计质量变差，这时该更频繁地同步 sampling 策略、缩小更新。

常有人说「GRPO 已经 on-policy，所以不需要 $\rho$」。严格的 on-policy 每步都用当前 $\pi_\theta$ sampling，实际训练做不到。数据来自 $\pi_{\mathrm{old}}$，目标却是 $\pi_\theta$，令

$$
\rho_t=\frac{\pi_\theta(y_t\mid x,y_{\lt t})}{\pi_{\mathrm{old}}(y_t\mid x,y_{\lt t})}.
$$

surrogate $\mathbb{E}_{\pi_{\mathrm{old}}}[\rho_t A_t]$ 在 $\theta=\theta_{\mathrm{old}}$ 处一阶等于真实的 on-policy 梯度，所以可以小步复用这批数据，PPO/GRPO 再用 clip 把有利方向上过大的 $\rho$ 削平。没有 $\rho$，就等于假装新策略采出了旧轨迹，epoch 稍多一点就偏了。公式在 loss 里的位置见 `ali-grpo-loss`，和 KL reference distribution 的关系见 `ali-grpo-kl-vs-ppo`。

新旧策略差很大时，$\rho$ 的极端值变多，方差上升；clip 大量生效，有效更新变少；偏差和方差一起恶化，训练不稳。fresh rollout 的要求在 GRPO 里同样成立，epoch 过多、ratio 偏离，$\rho$ 一样会数值异常。所以监控别光看 reward，要看 $\rho$ 的分位数、clip 触发率、相对 $\pi_{\mathrm{old}}$ 的 KL。clip 触发率接近 1，说明这批数据已经不值得再训了。组内 $A$ 算得再准，也救不了 $\rho$ 爆炸，那是另一条轴（`ali-grpo-advantage`），改变不了「这批轨迹已经代表不了当前策略」这件事。

应对办法是缩短 sync 间隔，也就是更频繁地 rollout，再减小学习率 / clip 范围，监控 KL 和 $\rho$ 分布，必要时 resampling。缩短 sync、减小 $\varepsilon$ 之外的更新幅度，都比把 clip 区间开大更安全。开大 clip 等于承认 surrogate 还可信，可通常它已经不可信了。GSPO 把 $\rho$ 收到序列级再 clip，改的是粒度，importance sampling 还在（[arXiv:2507.18071](https://arxiv.org/abs/2507.18071)）。

## 追问

**$\rho$ 可以截断当 mask 用吗？**
截断会引入偏差。PPO 的做法是 clip 目标函数，没有把真实概率比强行塞进区间。

**完全 off-policy 复用旧轨迹行不行？**
需要更稳的修正，比如截断 IS、V-trace 一类。LLM 上更常见的做法是缩短 off-policy 的程度，很少上复杂修正。

**$\rho$ 和 drift KL 是一回事吗？**
不是。$\rho$ 相对 $\pi_{\mathrm{old}}$，drift KL 相对冻结的 $\pi_{\mathrm{ref}}$。
