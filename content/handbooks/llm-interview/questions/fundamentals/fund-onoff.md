---
id: fund-onoff
section: fundamentals
order: 6
level: A
title: On-policy vs Off-policy；PPO/GRPO 为什么强调 Fresh Rollout？
quick: "PPO/GRPO 要估的是当前策略的梯度，数据最好就由当前策略来采。旧轨迹要靠重要性比率修正分布差异，LLM 的回答又是很长的 token 序列，比率连乘后方差很容易失控，所以默认及时采新的 rollout，只在 clip 范围内少量复用。"
tags:
  - RL
  - On-policy
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: Proximal Policy Optimization Algorithms
    url: https://arxiv.org/abs/1707.06347
    type: primary
  - title: DeepSeekMath — GRPO
    url: https://arxiv.org/abs/2402.03300
    type: secondary
---

PPO 和 GRPO 强调 fresh rollout，是因为它们估的是当前策略 $\pi_\theta$ 的梯度，数据离当前策略越远，用来修正的重要性比率就越不可靠，而 LLM 的回答很长，这个比率会随 token 数连乘放大。所以它们允许少量复用旧数据，默认还是要尽快用新策略重新采样。

先把两个词说清楚。On-policy 指采数据的行为策略就是当前策略，或者只差几次更新；off-policy 指数据来自旧策略、人类或者别的模型。用 off-policy 数据可以，但必须做分布修正，不修正，算出来的就是别的策略的梯度。重要性采样的原理见 `fund-is`、`ali-importance-sampling`。

举个例子：拿一周前 SFT 模型生成的一批数学解答，直接当 GRPO 的 group 去算优势。这些回答来自旧模型的分布，当前模型可能早就不那样写了，组内谁好谁坏的排序也已经过时。

## 为什么长 token 序列特别怕旧轨迹

一条回复的概率是 $T$ 个 token 条件概率的乘积，所以重要性比也是连乘：

$$
\rho=\frac{\pi_\theta(y\mid x)}{\pi_{\mathrm{old}}(y\mid x)}=\prod_{t=1}^{T}\frac{\pi_\theta(y_t\mid x,y_{\lt t})}{\pi_{\mathrm{old}}(y_t\mid x,y_{\lt t})}
$$

旧策略每步只要偏一点，连乘下来 $\rho$ 要么爆炸、要么接近 $0$，方差就失控了。LLM 的 $T$ 可达数百到数千，比经典控制里的短轨迹苛刻得多，所以 fresh rollout，也就是用当前或刚同步过的策略在环境里重新采样，几乎是默认纪律。

PPO 论文允许在同一批 rollout 上跑多个 epoch，这是有意的轻度 off-policy：$\pi_{\mathrm{old}}$ 和 $\pi_\theta$ 离得很近，clip 把过大的 $\rho$ 截掉。epoch 太多或者 actor 更新太快，clip fraction 就会飙升、KL 恶化，相当于拿错的数据硬训。GRPO 没有价值评估模型（critic），靠组内相对优势，对过期策略更敏感：旧组里的相对好坏，换成新的 $\pi$ 之后可能是颠倒的。旧数据还更容易整组全对或全错，这时优势全为零（`byte-grpo-all-same-zero-adv`）。

## 怎么判断够不够新鲜

看指标，别凭感觉说「刚采过」。盯 clip fraction、approx KL 和有效样本 ESS，这几个坏了，就先减 epoch、更勤地同步权重、换新的采样轨迹（rollout），加大学习率解决不了问题（`fund-pg-ppo-grpo-index`）。

复用旧数据也能做。Replay 能提高 sample efficiency，代价是要解决三件事：ratio 修正、value 外推，以及轨迹里的状态和当前环境对不上。Agent 场景最麻烦，工具结果、页面、库存、账户状态、API 都会变，旧观测结果（observation）对应的最优动作可能已经变了，有的旧轨迹根本没法回放。ratio 修的是策略差，修不了环境差。

几种常见的错用：把一周前的监督微调（SFT）轨迹当 GRPO group；做了 off-policy 只报「复用了所以省钱」，不报 ESS；环境版本已经变了还在 replay。Replay、离线强化学习（RL）、用人类轨迹这些 off-policy 方法都能做，前提是显式修正，或者承认有偏差。序列上 $\rho$ 是连乘，所以才会有截断 IS、V-trace 这类方法。直接偏好优化（DPO）用的是静态偏好对，是另一条 off-policy 路线，没有 online rollout，别和 PPO 的 fresh 要求混在一起。估当前梯度就尽量用当前数据；用别人的数据，就要付方差或偏差的代价。

## 追问

**PPO 到底算 on-policy 还是 off-policy？**
算轻度 off-policy。它允许少量旧样本加 clip，精神上仍是 on-policy，靠数据新鲜让 ratio 保持在 $1$ 附近。

**DPO 呢？**
DPO 用静态偏好对，是 off-policy 的偏好学习，没有 online rollout，和 PPO 的 fresh 要求是两回事。

**为什么 Agent 更需要 fresh？**
因为环境本身是非平稳的。旧 observation 对应的最优动作已经变了，ratio 修的是策略差，修不了环境差。

**几个 epoch 算多？**
没有普适数字，看 clip fraction 和 KL。指标恶化就减，用不着背「必须 $1$ 个 epoch」。

**旧轨迹完全不能用吗？**
能用，可以当 SFT 示范，或者经过验证器（verifier）检查后当离线偏好数据。别直接把它当成当前 $\pi$ 的 group 去算 GRPO 优势。

相关：`fund-pg-ppo-grpo-index`、`pt-pg-to-ppo-to-grpo`
