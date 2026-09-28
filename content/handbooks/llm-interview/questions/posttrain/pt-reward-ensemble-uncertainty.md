---
id: pt-reward-ensemble-uncertainty
section: posttrain
order: 230
level: S
title: Reward ensemble 如何估计不确定性，并用于抑制 overoptimization？
quick: >-
  单 RM 高分不等于可靠。用 ensemble 的均值作回报、分歧作不确定性，对高方差区域降权、拒训或保守更新，
  能减缓对代理奖励的过拟合；标准差不是校准好的人类偏好概率。
tags:
  - Reward Model
  - Ensemble
  - Uncertainty
  - Overoptimization
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Helping or Herding? Reward Model Ensembles Mitigate but do not Eliminate Reward Hacking
    url: https://arxiv.org/abs/2312.09244
    type: primary
  - title: Reward Model Ensembles Help Mitigate Overoptimization
    url: https://arxiv.org/abs/2310.02743
    type: secondary
---

这块容易把单 RM 高分当成「人类也会打高分」，再把 ensemble 标准差当成已经校准的概率。$\hat r$ 是偏好的有噪代理；策略优化它时会走向 RM 外推最乐观、真实偏好未必认同的区域，即 reward overoptimization。Coste 等表明 ensemble 能推迟这条崩点；Eisenstein 等接着说 mitigate 不等于 eliminate。成员相关时 $\sigma$ 会虚假偏低，hacking 仍在。

## 均值当回报，分歧当拒训信号

对同一 $(x,y)$ 得到 $\{r^{(k)}\}_{k=1}^{K}$，用

$$
\mu=\frac{1}{K}\sum_k r^{(k)},\qquad
\sigma^2=\frac{1}{K}\sum_k\bigl(r^{(k)}-\mu\bigr)^2.
$$

常见三种用法：（1）保守回报 $\mu-\lambda\sigma$ 再进 advantage；（2）$\sigma$ 高的样本降权、不进更新或回放到 SFT 分布；（3）ensemble 一致时才放大 KL 预算。$\lambda$ 过大则探索不足、能力涨不动；过小仍会 hacking 单个 RM 的盲点。这是 `pt-reward-ood-failure` 的工程化：OOD 常常表现为「某个 RM 异常乐观、其他成员不同意」，而不是训练曲线已经掉下去。成员数 $K$ 不必很大：3-5 个足够多样的模型，往往比 20 个同数据近邻 checkpoint 更有用。更新成员的节奏要慢于政策：政策每步都变，RM 集合每周重训一次，否则 $\sigma$ 跟踪的是优化噪声而不是外推风险。把 ensemble 分当 RL 的唯一奖励仍然危险。成员共有的 verbosity / 迎合偏差不会出现在 $\sigma$ 里，仍要独立 gold 或可执行 oracle。

成员必须多样：不同 seed、数据折、相距较远的 checkpoint，或权重平均。同一次 run 的相邻 checkpoint 相关性过高，$\sigma$ 会系统性低估。Dropout-at-test 或单模型 LoRA 多头便宜，但共享主干时 epistemic 覆盖仍然窄，只能当弱信号。Ensemble 不能替代 gold / held-out human：对比曲线必须画 proxy $\mu$ 对 gold，而不是只看训练 RM 单调上升。Gao 式 overoptimization 图在 ensemble 下仍然要画，只是崩点可能被推后。Best-of-N 若用 $\mu$ 选、不看 $\sigma$，等于在高分歧区挑最乐观的幻觉；保守选点应用 $\mu-\lambda\sigma$ 或「全体成员都高于阈值」。

## 高分歧样本怎么处置

问答 RL 里「华丽但空洞」常让某一个 RM 打高分、另外两个明显偏低。$\sigma$ 尖峰应触发人工抽检或拒用该 batch 的极端高分，而不是平均掉继续训。高 $\mu$ 低 $\sigma$ 才是相对可信的强化区；高 $\mu$ 高 $\sigma$ 优先当 OOD 候选。成员若共享同一标注偏差（都偏爱长答案），$\sigma$ 低也不能证明可靠。那是共有 bias，不是校准好的置信度。Label noise 会抬高所有成员的抖动，不代表该样本更 OOD：同一 $(x,y)$ 在不同数据折上分数都散，更像标注不稳；只在某一折 / 某一 seed 上飞，才像外推。实践上把高 $\sigma$ 队列给人审或更严 verifier，确认后再决定是拒训、降权还是补标。KL 加大只能推迟离开 $\pi_{\mathrm{ref}}$，发现不了「所有成员一起被同一捷径骗走」；那种共谋要用独立 gold，不能靠再加一个同族 RM。

ensemble 是保守更新和审计开关，不是把 $\sigma$ 当成 $p(\text{human prefers})$。成员相关、标签噪声和 epistemic 分歧要分开讲。proxy 单调上升而 gold 与 $\sigma$ 同时恶化，就是 overoptimization 的仪表盘，不要再加步数。

## 追问

- **$\sigma$ 是校准概率吗？** 不是。它是成员分歧，混有 epistemic 不确定和 label noise。高相关成员会让 $\sigma$ 虚假偏低。
- **和单 RM + 大 KL？** KL 只推迟离开 $\pi_{\mathrm{ref}}$，不检测盲点；ensemble 分歧是检测信号。二者互补，见 `pt-reward-ood-failure`。
- **权重平均算不算 ensemble？** 算弱 ensemble，便宜但多样性通常不够；关键仍是成员是否看见不同数据或初始化。
- **$\lambda$ 怎么调？** 看 gold 曲线：proxy 还在涨、gold 已掉就加大保守；能力平台期且 $\sigma$ 普遍很高，说明探索被掐死，应减小 $\lambda$ 或给成员加多样性。
