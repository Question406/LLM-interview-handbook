---
id: fund-onoff
section: fundamentals
order: 6
level: A
title: On-policy vs Off-policy；PPO/GRPO 为什么强调 Fresh Rollout？
quick: >-
  On-policy 用当前 policy 数据估当前 policy gradient；off-policy 用其他 behavior policy
  数据，需要 correction。LLM 序列分布维度极高，旧 trajectory 的 importance
  ratio 很快高方差。
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

错法：PPO/GRPO「完全不能复用旧数据」，或者 off-policy「有 replay 就更先进」。核心是：你要估的是当前 $\pi_\theta$ 的梯度，数据却来自谁。On-policy：行为策略就是当前策略（或只差几次更新）。Off-policy：数据来自旧策略、人类、或别的模型，必须做分布修正，否则梯度是错的。重要性采样见 `fund-is`、`ali-importance-sampling`；算法谱系见 `fund-pg-ppo-grpo-index`、`pt-pg-to-ppo-to-grpo`。

## 为什么 token 序列特别怕旧轨迹

一条回复是 $T$ 个 token 的联合分布，重要性比

$$
\rho=\frac{\pi_\theta(y\mid x)}{\pi_{\mathrm{old}}(y\mid x)}=\prod_{t=1}^{T}\frac{\pi_\theta(y_t\mid x,y_{\lt t})}{\pi_{\mathrm{old}}(y_t\mid x,y_{\lt t})}
$$

随 $T$ 连乘，旧策略稍一偏，$\rho$ 不是爆炸就是接近 $0$，方差失控。这就是「fresh rollout」：用当前（或刚同步的）政策在环境里重新采样。PPO 用 clip 的 importance ratio 允许 小段 复用 old-policy samples；epoch 太多或 actor 更新太快，clip fraction 飙升、KL 恶化，等于在用错数据硬训。GRPO 同样吃组内相对优势，组若来自过期政策，排序会过时。

## Off-policy 能用，但账要算清

Replay 提高 sample efficiency，但要解决：ratio 修正、value 外推、轨迹状态与当前环境不一致。Agent 里工具结果、页面、账户状态会变，旧轨迹甚至不可回放，比单轮对话更难。监控：clip fraction、approx KL、有效样本（ESS）。这些指标坏了，优先减 epoch、加同步频率、换新 rollout，而不是加大学习率。组内全同则优势为零（`byte-grpo-all-same-zero-adv`），旧数据更容易全同。

失败模式：把一周前的 SFT 轨迹当 GRPO group；off-policy 不报 ESS 只报「复用了所以省钱」；环境版本变了还在 replay。

## Fresh 到什么程度才算够

PPO 论文允许在同一批 rollout 上做多个 epoch，这是有意的轻度 off-policy：$\pi_{\mathrm{old}}$ 与 $\pi_\theta$ 很近，clip 把过大的 $\rho$ 截断。实践里「够新鲜」看的是 clip fraction、approx KL、有效样本 ESS，而不是看你主观上「刚采过」。这些指标坏了，优先减 epoch、更勤同步权重、换新 rollout（`fund-pg-ppo-grpo-index`）。GRPO 没有 critic，组内排序对过期政策更敏感：旧组里的相对好坏，换了新 $\pi$ 可能颠倒。Agent 还多一个环境非平稳：页面、库存、API 变了，旧 observation 对应的最优动作已经变，ratio 修的是策略差，修不了环境差。

Off-policy 方法（replay、离线 RL、用人类轨迹）不是不能做，但必须显式修正或承认偏差。重要性采样见 `fund-is`。序列上 $\rho$ 连乘，截断 IS 或 V-trace 一类方法才会出现。DPO 用静态偏好对，是另一条 off-policy 路，没有 online rollout，不要和 PPO 的 fresh 要求混为一谈。估当前梯度就尽量用当前数据；用别人的数据就要付方差或偏差的代价。

LLM 的 $T$ 可达数百到数千，比经典控制里的短轨迹苛刻得多，「fresh rollout」几乎是默认纪律。

## 追问

- **PPO 到底 on 还是 off？** 轻度 off-policy：允许少量旧样本 + clip；精神是 on-policy，靠 freshness 保 ratio 靠近 $1$。
- **DPO 呢？** 用静态偏好对，是 off-policy 偏好学习，没有 online rollout，和 PPO 的 fresh 不是同一约束。
- **Agent 为什么更要 fresh？** 环境非平稳，旧 observation 对应的最优动作已经变了，ratio 修的是策略差，修不了环境差。
- **几个 epoch 算多？** 没有普适数字；看 clip fraction 和 KL。指标恶化就减，而不是背「必须 $1$ 个 epoch」。
- **旧轨迹完全不能用吗？** 可当 SFT 示范或经过 verifier 的离线偏好，不要直接当当前 $\pi$ 的 group 去算 GRPO 优势。
