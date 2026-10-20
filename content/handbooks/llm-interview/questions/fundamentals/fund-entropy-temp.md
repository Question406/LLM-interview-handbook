---
id: fund-entropy-temp
section: fundamentals
order: 11
level: A
title: Entropy Regularization 和 Sampling Temperature 有什么区别？
quick: "Temperature 改变采样轨迹（rollout）时的分布 $p_i\\propto e^{z_i/T}$，不直接改变训练目标。Entropy bonus 则将 $H(\\pi(\\cdot\\mid s))$ 加入损失，通过梯度改变策略参数。两者分别控制采样和训练，不能互相替代。"
tags:
  - RL
  - Sampling
  - Entropy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Softmax function — temperature
    url: https://en.wikipedia.org/wiki/Softmax_function#Smooth_argmax
    type: primary
  - title: Entropy regularization in RL (SAC)
    url: https://arxiv.org/abs/1801.01290
    type: secondary
---

常见误区是：两者都是「让模型更随机」。Temperature 改这一次怎么抽样；entropy bonus 改权重被训练成什么样。明天把温度调回去，策略立刻复原；entropy bonus 写进损失后，存盘的 $\pi$ 已经变了。熵的定义见 `fund-shannon-entropy`，softmax 与 NLL 见 `fund-softmax-nll`。训练时熵塌缩是数据/奖励问题，见 `data-entropy-collapse`；确认是坏塌之后的旋钮顺序见 `data-entropy-fix-order`。

## Temperature（推理 / 采样轨迹（rollout））

$$
\pi_T(a\mid s)=\frac{\exp(z_a/T)}{\sum_{a'}\exp(z_{a'}/T)}.
$$

$T=1$ 是训练时的 softmax。$T\to 0$ 趋近 greedy；$T\to\infty$ 趋近均匀。它不改网络参数，只改用这组 logits 怎么抽样。评测对比必须锁 $T$，否则把采样噪声当成算法增益。Agent rollout 提高 $T$ 可以多探索，但若梯度里的 $\log\pi$ 仍按 $T=1$ 计算，这只影响采集到的轨迹，不直接等于「训练更随机」。

## Entropy regularization（训练）

策略梯度目标多一项：

$$
J(\theta)=\mathbb{E}_{\pi_\theta}[R]+\alpha\,\mathbb{E}_{s\sim\pi}\big[H(\pi_\theta(\cdot\mid s))\big],
$$

其中 $H(\pi(\cdot\mid s))=-\sum_a\pi(a\mid s)\log\pi(a\mid s)$。对 $\theta$ 求导会多出 $\alpha\nabla_\theta H$。模型被训练成更平或更尖。SAC 以及部分 LLM 强化学习（RL）将 $\alpha$ 做成可学习或按目标熵调节，控制的是这条 bonus，不是采样温度。KL 约束与探索的另一面见 `pt-kl-direction-and-exploration`：反向 KL 会压探索，和加熵是相反方向的力。

## 可以同时用，但不是同一个旋钮

高 $T$ 只让这一次 rollout 更散；除非把 $T$ 编进计算图（会改变 entropy 的尺度，必须说清楚），否则梯度仍对训练时的 $T=1$ 分布。Entropy bonus 即使推理永远 greedy，训练过的 $\pi$ 也可能比没加 bonus 时更分散。监控看训练曲线上的 policy entropy，不要只看采样 $T$。熵塌缩但奖励分数（reward）虚高，优先查 bonus 是否过小、KL 是否过松、数据是否全变成易题，而不是先把 $T$ 调到 $1.5$。

失败模式：用高温解码当「探索算法」去对标 on-policy RL；把评测 $T$ 和训练 $T$ 混用导致不可复现。

## 监控时看哪条曲线

训练日志里的 policy entropy 是 $H(\pi_\theta(\cdot\mid s))$ 的经验均值，对应的是当前权重下 $T=1$ 的分布，不是你采样时设的 $T$。这条曲线塌了，说明策略变尖：GRPO 组内答案趋同、PPO 的 ratio 靠近边界、奖励可能来自格式投机。此时先查 $\alpha$ 是否过小、KL 是否过松、数据是否全是易题（`data-entropy-collapse`），而不是把 rollout 温度调到 $1.5$ 掩盖策略已经变尖的问题。高温 rollout 采到的轨迹更散，但若优势估计和 $\log\pi$ 仍对 $T=1$，你只是在用噪声更大的数据估计同一策略的梯度，方差往往更大，不等于加了熵正则。

反过来，entropy bonus 过大，策略接近均匀，reward 学不动，像在随机乱采样。SAC 用目标熵调节 $\alpha$，LLM RL 更常见的是固定小 $\alpha$ 再靠 KL 锚住 $\pi_{\mathrm{ref}}$。两者同时出现时量纲不同：KL 是相对参考策略，熵是相对均匀分布，不要合成一个「随机度」旋钮。评测必须锁 $T$（常见 $0$ 或 $1$）；用训练时的高温去报分数，会把随机性当成能力。

## 追问

- **推理 greedy 还能有熵 bonus 的效果吗？** 有。权重已经变，greedy 下的峰值也可能更平、更不易锁死单一模板。
- **和 KL penalty 什么关系？** KL 把 $\pi$ 拉向参考策略；熵 bonus 把 $\pi$ 推向更均匀。常同时出现，量纲要分开调。
- **为什么 LLM RL 还要看 entropy 曲线？** 熵过早塌缩意味着组内无方差、GRPO/PPO 没信号。先查是不是坏塌（`data-entropy-collapse`），再按有效组 → clip → 长度 → 熵正则动手（`data-entropy-fix-order`），不要先把温度调到 $1.5$。
- **能不能把 $T$ 编进训练图？** 能，但 $H$ 的尺度会变，$\alpha$ 要重调；多数实现训练固定 $T=1$，只在 rollout 改 $T$。
- **高温采样算 off-policy 吗？** 若 $\log\pi$ 按 $T=1$ 算而数据来自 $T\neq 1$，严格说行为策略变了，应用 IS 或承认偏差；工程上小偏移常被忽略，这一点我会点出来。
