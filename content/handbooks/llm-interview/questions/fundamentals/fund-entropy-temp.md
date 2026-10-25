---
id: fund-entropy-temp
section: fundamentals
order: 11
level: A
title: Entropy Regularization 和 Sampling Temperature 有什么区别？
quick: "Temperature 只改这一次怎么从 logits 抽样，不动参数，调回去策略就复原；entropy bonus 写进损失，改的是权重被训练成什么样。两者可以同时用，但量纲和作用对象不同：评测要锁 $T$，训练看 policy entropy 曲线。"
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
Temperature 改的是这一次怎么抽样，entropy bonus 改的是权重被训练成什么样，所以「两者都是让模型更随机」这个说法不准。明天把温度调回去，策略马上复原；entropy bonus 写进损失以后，存盘的 $\pi$ 已经变了。熵的定义见 `fund-shannon-entropy`，softmax 和 NLL 见 `fund-softmax-nll`。

举个例子，同一个 checkpoint，用 $T=0$ 和 $T=1.5$ 各跑一遍评测，分数可能不同，因为解码时使用的分布变了，模型参数仍然相同。加了 entropy bonus 训练后，参数本身会改变；即使推理时始终用 greedy，模型的输出分布也可能比没加时更分散。

## Temperature（推理 / 采样轨迹（rollout））

$$
\pi_T(a\mid s)=\frac{\exp(z_a/T)}{\sum_{a'}\exp(z_{a'}/T)}.
$$

$T=1$ 就是训练时的 softmax。$T\to 0$ 趋近 greedy，$T\to\infty$ 趋近均匀。它不改网络参数，只改用这组 logits 怎么抽样，所以评测对比必须锁死 $T$，否则会把采样噪声当成算法增益。Agent rollout 时调高 $T$ 可以多探索，但如果梯度里的 $\log\pi$ 仍按 $T=1$ 算，它只影响采到了哪些轨迹，并不等于「训练更随机」。

## Entropy regularization（训练）

策略梯度的目标多了一项：

$$
J(\theta)=\mathbb{E}_{\pi_\theta}[R]+\alpha\,\mathbb{E}_{s\sim\pi}\big[H(\pi_\theta(\cdot\mid s))\big],
$$

其中 $H(\pi(\cdot\mid s))=-\sum_a\pi(a\mid s)\log\pi(a\mid s)$。对 $\theta$ 求导会多出 $\alpha\nabla_\theta H$，模型被训练得更平或更尖。SAC 和部分 LLM 强化学习（RL）把 $\alpha$ 做成可学习的，或按目标熵调节，控制的都是这条 bonus，跟采样温度无关。KL 约束和探索的关系见 `pt-kl-direction-and-exploration`：反向 KL 会压探索，和加熵是方向相反的两股力。

## 可以同时用，但别当成同一个旋钮

高 $T$ 只让这一次 rollout 更散。除非把 $T$ 编进计算图（这会改变 entropy 的尺度，必须说清楚），梯度对应的仍是训练时 $T=1$ 的分布。

训练日志里的 policy entropy，是当前权重下 $T=1$ 分布的 $H(\pi_\theta(\cdot\mid s))$ 经验均值，跟采样时设的 $T$ 无关。这条曲线塌了，说明策略变尖了：GRPO 组内答案趋同，PPO 的 ratio 贴近边界，奖励可能来自格式投机。熵塌缩但奖励分数（reward）虚高时，先查 $\alpha$ 是否过小、KL 是否过松、数据是否全变成了易题（`data-entropy-collapse`），别先把 rollout 温度调到 $1.5$ 去掩盖策略已经变尖的事实。确认是坏塌之后的处理顺序见 `data-entropy-fix-order`。高温 rollout 采到的轨迹更散，但如果优势估计和 $\log\pi$ 仍按 $T=1$ 算，只是在用噪声更大的数据估同一个策略的梯度，方差往往更大，效果也跟加熵正则不一样。

反过来，entropy bonus 太大，策略接近均匀，reward 学不动，像在随机乱采。SAC 用目标熵调节 $\alpha$，LLM RL 更常见的是固定一个小 $\alpha$，再用 KL 锚住 $\pi_{\mathrm{ref}}$。两者同时出现时量纲不同：KL 相对参考策略，熵相对均匀分布，别把它们合成一个「随机度」旋钮。

常见的失败模式有两种：用高温解码当「探索算法」去对标 on-policy RL；评测 $T$ 和训练 $T$ 混用，结果不可复现。评测必须锁 $T$（常见 $0$ 或 $1$），拿训练时的高温去报分数，会把随机性当成能力。

## 追问

**推理用 greedy，还能有熵 bonus 的效果吗？**
有。权重已经变了，greedy 下的峰值也可能更平，不容易锁死在单一模板上。

**和 KL penalty 什么关系？**
KL 把 $\pi$ 拉向参考策略，熵 bonus 把 $\pi$ 推向更均匀。两者常一起出现，量纲要分开调。

**为什么 LLM RL 还要盯 entropy 曲线？**
熵过早塌缩意味着组内没有方差，GRPO / PPO 拿不到信号。先查是不是坏塌（`data-entropy-collapse`），再按有效组 → clip → 长度 → 熵正则的顺序动手（`data-entropy-fix-order`），别先把温度调到 $1.5$。

**能不能把 $T$ 编进训练图？**
能，但 $H$ 的尺度会变，$\alpha$ 要重调。多数实现训练时固定 $T=1$，只在 rollout 时改 $T$。

**高温采样算 off-policy 吗？**
如果 $\log\pi$ 按 $T=1$ 算、数据却来自 $T\neq 1$，严格说行为策略变了，应该用 IS 或者承认有偏差。工程上小的偏移常被忽略，这一点我会主动点出来。
