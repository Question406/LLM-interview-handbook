---
id: fund-passk
section: fundamentals
order: 18
level: A
title: Pass@k 怎么估？为什么不能直接看 k 次中至少一次成功的样本均值？
quick: >-
  每题采 $n$ 条、其中 $c$ 条正确时，用 unbiased estimate
  $1-\binom{n-c}{k}/\binom{n}{k}$（$n-c\ge k$，否则为 1）。它把 $n$ 条全用上，比只看前 $k$
  次有没有对更稳；$1-(1-c/n)^k$ 是有放回近似，会偏。
tags:
  - Eval
  - Coding
  - Pass@k
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: Evaluating Large Language Models Trained on Code
    url: 'https://arxiv.org/abs/2107.03374'
    type: primary
---

Pass@k 用 HumanEval / Codex 那套无放回组合估计：每题采 $n$ 条、判出 $c$ 条正确，算「从这 $n$ 条里随机抽 $k$ 条、至少一条正确」的概率。直接看 $k$ 次里有没有成功也能算，只是浪费样本。最常见的错有两个：把「$n$ 次里出现过一次正确」当成 $\mathrm{pass@}k$，那其实是 $\mathrm{pass@}n$；以及拿 $1-(1-\hat p)^k$ 当 unbiased estimate。

## 无偏公式

每题独立采 $n$ 个 completion，判对 $c$ 个。若 $n-c\lt k$，怎么抽 $k$ 条都至少有一个对，估计就是 $1$。否则

$$
\widehat{\mathrm{pass@}k}=1-\frac{\binom{n-c}{k}}{\binom{n}{k}}.
$$

分子是抽到的 $k$ 条全落在 $n-c$ 条错解里的组合数，这是超几何分布：不放回、有限总体。对所有题取平均，就是数据集上的 $\mathrm{pass@}k$。实现时用乘积，避免大组合数溢出：

$$
\frac{\binom{n-c}{k}}{\binom{n}{k}}=\prod_{i=0}^{k-1}\frac{n-c-i}{n-i}.
$$

两个 edge cases 可以顺手验证：$n=c=k=1$ 时就是普通准确率，$c=0$ 时恒为 $0$。

## 为什么不直接看前 $k$ 次

只看每题前 $k$ 个样本有没有对，也是一个无偏的 Bernoulli 估计，可后面 $n-k$ 条的信息全丢了，方差更大。比如每题已经采了一大批，只看前几条，后面那些对的错的都白采了。组合估计把 $n$ 条全用上，同样的计算预算下更稳。所以标题里那个做法可以用，只是浪费样本。

有放回近似 $1-(1-c/n)^k$ 在 $n$ 不大、$k$ 相对 $n$ 不小时会偏高，因为它允许重复抽到同一条正确解。白板上先写无放回的版本，再说这个近似只在 $n\gg k$ 时接近。

## 怎么报、怎么读

$\mathrm{pass@}1$ 和 $\mathrm{pass@}k$ 要一起报，并写清 $n$、$k$、温度和是否去重。$\mathrm{pass@}1$ 升、$\mathrm{pass@}k$ 不动，常常是多样性塌了，模型只是把已有的正确模式采得更勤，见 `pt-rlvr-reasoning-eval`、`pt-dpo-to-grpo`；反过来 $\mathrm{pass@}k$ 升、$\mathrm{pass@}1$ 不动，说明覆盖变宽了，但缺一个选择器。

跨题汇总仍要给 confidence interval，题数少时 point estimate 波动较大。`temperature`、`top_p`、是否对相同 completion 去重，都会改变 $c$；去重后 $n$ 也变小了，要用去重后的 $n,c$ 重算，别拿去重前的分母。Best-of-$N$、验证器（verifier）rerank、majority vote 都是选择器，应该另列，别塞进同一个 $\mathrm{pass@}k$，后者假设的是 $k$ 次独立 sampling、命中即可。

开始 GRPO 训练前，可以先看 $\mathrm{pass@}k-\mathrm{pass@}1$ 的缺口：缺口还在，组内才可能有相对优势；缺口已经是 0，再加大 $G$ 也只是全对组，见 `meituan-sft-to-rl-gate`。

## 追问

**$n\lt k$ 怎么办？**
就不报这个 $k$。定义要求 $n\ge k$，采不够就继续采满。

**avg@32 和 $\mathrm{pass@}32$ 是一回事吗？**
不是。avg@32 是 32 次独立作答的平均准确率，近似 $\mathrm{pass@}1$ 的低方差估计。DAPO 在 AIME 上用的是 avg@32，定义别混。

**这个估计相对什么无偏？**
相对「从这 $n$ 条有限样本里再抽 $k$ 条」的成功概率。它对应的还不是真实生成分布下的 $k$ 次独立试验，后者还取决于温度是否和训练时一致。

**代码题的 $c$ 怎么数？**
以单元测试或官方 checker 为准。拿 LLM judge 冒充 $c$，$\mathrm{pass@}k$ 衡量的就只是答案看起来是否正确，见 `fund-judge`。
