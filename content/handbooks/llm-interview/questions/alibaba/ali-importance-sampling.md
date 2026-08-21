---
id: ali-importance-sampling
section: alibaba
order: 5
level: A
title: GRPO/PPO 为何需要重要性采样？新旧策略差很大时还有用吗？
quick: 因为用旧策略采样的轨迹估计新策略目标，需要 $\rho$ 校正。差太大时 $\rho$ 方差爆炸、clip 频繁触发，估计质量变差，应更频繁同步采样策略或缩小更新。
tags:
  - Alibaba
  - GRPO
  - PPO
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-19
sources:
  - title: ↗ 阿里国际大模型算法一面
    url: 'https://www.nowcoder.com/feed/main/detail/27a27fc44b8a4613ae790ba27add8850'
    type: legacy-reference
---

陷阱是说「GRPO 已经 on-policy，所以不需要 $\rho$」。真正的 on-policy 每步都用当前 $\pi_\theta$ 采样；工程上几乎总是 **近似 on-policy**：用 $\pi_{\mathrm{old}}$ rollout，用 $\pi_\theta$ 更新多个 epoch。重要性比把贡献校正回当前策略。差太大时 $\rho$ 方差爆炸、clip 频繁触发，估计质量变差。公式落点见 `ali-grpo-loss`，和 KL 锚点的关系见 `ali-grpo-kl-vs-ppo`。

## 为什么要 $\rho$

数据来自 $\pi_{\mathrm{old}}$，目标却是 $\pi_\theta$。令

$$
\rho_t=\frac{\pi_\theta(y_t\mid x,y_{\lt t})}{\pi_{\mathrm{old}}(y_t\mid x,y_{\lt t})}.
$$

surrogate $\mathbb{E}_{\pi_{\mathrm{old}}}[\rho_t A_t]$ 在 $\theta=\theta_{\mathrm{old}}$ 处一阶等于真实 on-policy 梯度，所以可以小步复用这批数据。PPO/GRPO 再用 clip 把有利方向上过大的 $\rho$ 削平。没有 $\rho$ 等于假装新策略采样了旧轨迹，epoch 稍多就偏。

## 差很大时：不是「还能用」，是估计坏了

当新旧策略差很大：$\rho$ 极端值增多，方差上升；clip 大量生效，有效更新变少；偏差/方差同时恶化，训练不稳。工程应对：缩短 sync 间隔（更频繁 rollout）、减小学习率/clip 范围、监控 KL 与 $\rho$ 分布、必要时重采样。组内 $A$ 再准，也救不了 $\rho$ 爆炸——那是另一轴（`ali-grpo-advantage`）。GSPO 把 $\rho$ 收到序列级再 clip，改的是粒度，不是取消重要性采样（[arXiv:2507.18071](https://arxiv.org/abs/2507.18071)）。

Fresh rollout 在 GRPO 里仍然成立：epoch 过多、ratio 偏离，$\rho$ 一样会炸。监控不要只看 reward；看 $\rho$ 的分位数、clip 触发率、相对 $\pi_{\mathrm{old}}$ 的 KL。clip 触发率接近 1 说明这批数据已经不值得再训。组内 $A$ 再漂亮，也改变不了「这批轨迹已经不能代表当前策略」。缩短 sync、减小 $\varepsilon$ 之外的更新幅度，比把 clip 区间开大更安全——开大 clip 等于承认 surrogate 仍可信，通常并不可信。

## 追问

- **$\rho$ 可以截断当 mask 吗？** 截断会引入偏差。PPO 的做法是 clip **目标函数**，不是把真实概率比强制塞进区间。
- **完全 off-policy 复用旧轨迹？** 需要更稳的修正（截断 IS、V-trace 一类）。LLM 上更常见的是缩短 off-policy 程度，而不是上复杂修正。
- **和 drift KL 是一回事吗？** 不是。$\rho$ 相对 $\pi_{\mathrm{old}}$；drift KL 相对冻结 $\pi_{\mathrm{ref}}$。
