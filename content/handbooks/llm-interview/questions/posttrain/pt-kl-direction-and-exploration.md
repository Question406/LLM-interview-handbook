---
id: pt-kl-direction-and-exploration
section: posttrain
order: 41
level: S
title: 为什么常见 reverse-KL reference regularization 可能让 RLVR 困在 base-model support？什么时候考虑不同 KL 方向或 reference reweighting？
quick: reverse KL 倾向留在 reference 的高概率模式附近，稳定但可能抑制稀有新策略。若高 K 表明好轨迹稀少且 reward 可靠，可探索更宽的正则或重加权；若 reward 噪声大，过度扩张会直接放大 hacking。
tags:
  - KL
  - Exploration
  - RLVR
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: Unlocking Reasoning via RL Exploration
    url: https://arxiv.org/abs/2510.03865
    type: primary
---

reference regularization 的目的不是数学装饰，而是在优化 reward 时限制语言退化和分布漂移。常见形式对新策略偏离 reference 的位置敏感，往往偏向 mode-seeking：安全、稳定，却会降低采样到稀有优质路径的机会。

决定是否放宽前，先测 reward 的 false positive、base policy 高 K coverage 和 OOD 回归。可尝试不同 KL 方向、动态系数、reference reweighting 或专门的 exploration phase，但每种改动都必须配合更强 verifier 和更密的 safety eval。

不能只看 Pass@1。要同时看 K 曲线、熵、模式多样性、长度、KL、reward 与真实成功率的偏离，否则容易把分布漂移误读成探索。
