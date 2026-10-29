---
id: pt-reward-ensemble-uncertainty
section: posttrain
order: 230
level: S
title: Reward ensemble 如何估计不确定性，并用于抑制 overoptimization？
quick: >-
  用 ensemble 的均值当回报、成员分歧当不确定性：对高分歧样本降权、拒训或用 $\mu-\lambda\sigma$
  保守更新，能推迟对代理奖励的过度优化。它只能缓解，成员共有的偏差不会出现在 $\sigma$ 里，$\sigma$ 也不是 calibration
  好的人类偏好概率。
tags:
  - Reward Model
  - Ensemble
  - Uncertainty
  - Overoptimization
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: >-
      Helping or Herding? Reward Model Ensembles Mitigate but do not Eliminate
      Reward Hacking
    url: 'https://arxiv.org/abs/2312.09244'
    type: primary
  - title: Reward Model Ensembles Help Mitigate Overoptimization
    url: 'https://arxiv.org/abs/2310.02743'
    type: secondary
---

做法是均值当回报、分歧当风险信号：同一个 $(x,y)$ 让几个 reward model（RM）打分，均值进 advantage，分歧大的样本降权、拒训或保守更新。这能推迟过度优化，消除不了，标准差也不能当成 calibration 好的 $p(\text{human prefers})$。

先说为什么要这么做。单个 RM 的 $\hat r$ 是偏好的有噪代理，策略优化它时，会往 RM 外推最乐观、真实偏好未必认同的区域走。比如问答 RL 里一段「华丽但空洞」的回答，一个 RM 打了高分，另外两个明显偏低，这就是外推区的典型样子。Coste 等发现 reward model 集成能推迟真实效果开始下降的时点；Eisenstein 等接着指出 mitigate 不等于 eliminate：成员相关时 $\sigma$ 会虚假偏低，hacking 照样发生。

具体来说，对同一个 $(x,y)$ 得到 $\{r^{(k)}\}_{k=1}^{K}$，算

$$
\mu=\frac{1}{K}\sum_k r^{(k)},\qquad
\sigma^2=\frac{1}{K}\sum_k\bigl(r^{(k)}-\mu\bigr)^2.
$$

常见用法有三种：保守回报 $\mu-\lambda\sigma$ 再进 advantage；$\sigma$ 高的样本降权、不进更新或回放到 SFT 数据分布；ensemble 一致时才放大 KL 预算。$\lambda$ 过大，探索不足、能力涨不动；过小，策略仍可能利用单个 RM 的盲点。这其实是 `pt-reward-ood-failure` 的工程化：out-of-distribution 样本（OOD）常常先表现为某个 RM 异常乐观、其他成员不同意，这时训练曲线还没掉下去。Best-of-N 也一样，用 $\mu$ 选、不看 $\sigma$，就是在高分歧区挑最乐观的 hallucination；保守的选法是 $\mu-\lambda\sigma$，或者「全体成员都高于阈值」。

成员一定要多样：不同 seed、不同数据折、相距较远的 checkpoint，或者权重平均。同一次 run 的相邻 checkpoint 相关性太高，$\sigma$ 会系统性低估。成员数 $K$ 不用很大，3-5 个足够多样的模型，往往比 20 个同数据的近邻 checkpoint 更有用。Dropout-at-test 或单模型 LoRA 多头很便宜，但共享主干，epistemic 覆盖还是窄，只能当弱信号。成员的更新节奏要慢于策略：策略每步都在变，RM 集合每周重训一次，否则 $\sigma$ 跟踪的是优化噪声，外推风险反映不出来。

高分歧样本要专门处置。$\sigma$ 出现尖峰时，应该触发人工抽检，或者拒用这个 batch 里的极端高分，平均掉接着训是最差的选择。高 $\mu$ 低 $\sigma$ 才是相对可信的强化区，高 $\mu$ 高 $\sigma$ 先当 OOD 候选。还要把标签噪声和外推分开：label noise 会抬高所有成员的抖动，同一个 $(x,y)$ 在不同数据折上分数都散，更像标注不稳；只在某一折或某一个 seed 上飞，才像外推。高 $\sigma$ 队列交给人审或更严格的验证器，确认后再决定拒训、降权还是补标。

ensemble 也有看不见的地方。成员共享同一个标注偏差，比如都偏爱长答案，$\sigma$ 低也证明不了可靠，那是共有 bias，成员共有的 verbosity / 迎合偏差都不会出现在 $\sigma$ 里。所有成员一起被同一条捷径骗走时，加大 KL 只能推迟离开 $\pi_{\mathrm{ref}}$，发现不了这种共同误判，要靠独立参考答案或可执行 oracle 去查，再加一个同族 RM 没用。所以把集成模型的分数当 RL 的唯一奖励仍然危险，对比曲线必须画 proxy $\mu$ 对 gold。Gao 式 overoptimization 图在 ensemble 下照样要画，只是崩点可能往后推了。proxy 单调上升、gold 和 $\sigma$ 同时恶化，就说明可能已经在过度优化代理奖励，别再加步数。

## 追问

**$\sigma$ 是 calibration 好的概率吗？**
不是。它是成员分歧，混着 epistemic 不确定性和 label noise，成员高度相关时还会虚假偏低。

**单 RM 加大 KL 能替代 ensemble 吗？**
替代不了。KL 只推迟离开 $\pi_{\mathrm{ref}}$，检测不到盲点；ensemble 分歧是检测信号。两者互补。

**权重平均算不算 ensemble？**
算弱 ensemble，便宜但多样性通常不够。关键还是成员有没有见过不同数据、用没用不同初始化。

**$\lambda$ 怎么调？**
看 gold 曲线。proxy 还在涨、gold 已经掉，就加大保守；能力到了平台、$\sigma$ 普遍很高，说明探索被掐死了，减小 $\lambda$ 或者给成员加多样性。
