---
id: fund-passk
section: fundamentals
order: 18
level: A
title: Pass@k 怎么估？为什么不能直接看 k 次中至少一次成功的样本均值？
quick: >-
  每题采 $n$ 条、其中 $c$ 条正确时，无偏估计是 $1-\binom{n-c}{k}/\binom{n}{k}$（$n-c\ge k$ 否则为 1）。它用满 $n$
  条，而不是只看前 $k$ 次有没有对；用 $1-(1-c/n)^k$ 是有放回近似，偏了。
tags:
  - Eval
  - Coding
  - Pass@k
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: Evaluating Large Language Models Trained on Code
    url: https://arxiv.org/abs/2107.03374
    type: primary
---

这块容易栽两处：把「$n$ 次里出现过一次正确」当成 $\mathrm{pass@}k$（那是 $\mathrm{pass@}n$）；以及用 $1-(1-\hat p)^k$ 当无偏估计。HumanEval / Codex 用的是 **无放回组合估计**：从已采的 $n$ 条里随机抽 $k$ 条、至少一条正确的概率。

## 无偏公式

每题独立采 $n$ 个 completion，判对 $c$ 个。若 $n-c\lt k$，怎么抽 $k$ 条都至少有一个对，估计就是 $1$。否则

$$
\widehat{\mathrm{pass@}k}=1-\frac{\binom{n-c}{k}}{\binom{n}{k}}.
$$

分子是「抽到的 $k$ 条全在 $n-c$ 条错解里」的组合数。这是超几何：不放回、有限总体。对题求平均得到数据集上的 $\mathrm{pass@}k$。实现上用乘积避免大组合数溢出：

$$
\frac{\binom{n-c}{k}}{\binom{n}{k}}=\prod_{i=0}^{k-1}\frac{n-c-i}{n-i}.
$$

$n=c=k=1$ 时就是普通准确率。$c=0$ 时恒为 $0$。

## 为什么不用「前 $k$ 次成功」的均值

只看每题前 $k$ 个样本有没有对，也是无偏的 Bernoulli，但 **方差更大**：你丢掉了后 $n-k$ 条信息。组合估计把 $n$ 条全用上，同一计算预算下更稳。这就是「不能直接看 $k$ 次中至少一次成功的样本均值」，可以看，只是浪费样本。

有放回近似 $1-(1-c/n)^k$ 在 $n$ 不大、$k$ 相对 $n$ 不小时会偏高：它允许重复抽到同一条正确解。白板先写无放回，再提这个近似只在 $n\gg k$ 时接近。

$\mathrm{pass@}1$ 升、$\mathrm{pass@}k$ 不动，常常是多样性塌了、只是把已有正确模式采得更勤，见 `pt-rlvr-reasoning-eval`、`pt-dpo-to-grpo`。反过来 $\mathrm{pass@}k$ 升、$\mathrm{pass@}1$ 不动，覆盖变宽但缺少选择器。两个数字要一起报，且写清 $n$、$k$、温度和是否去重。

## 评测协议

跨题汇总仍要置信区间；题数少时点估计会抖。`temperature`、`top_p`、是否允许相同 completion 去重，都会改 $c$。去重后 $n$ 变小，必须用去重后的 $n,c$ 重算，不能拿去重前的分母。Best-of-$N$、verifier rerank、majority vote 是 **选择器**，应另列，不要塞进同一个 $\mathrm{pass@}k$（后者假设 $k$ 次独立采样、命中即可）。

GRPO 进场前看 $\mathrm{pass@}k-\mathrm{pass@}1$：缺口还在，组内才可能有相对优势。缺口已经是 0，再加大 $G$ 也是全对组，见 `meituan-sft-to-rl-gate`。

## 追问

- **$n\lt k$ 怎么办？** 定义要求 $n\ge k$。采不够就不要报那个 $k$，或继续采满。
- **和 avg@32？** avg@32 是 32 次独立作答的平均准确率，近似 $\mathrm{pass@}1$ 的低方差估计，不是 $\mathrm{pass@}32$。DAPO 在 AIME 上用 avg@32，口径不要混。
- **无偏相对什么？** 相对「从这 $n$ 条有限样本里再抽 $k$ 条」的成功概率，不是相对真实生成分布的 $k$ 次独立试验，后者还依赖温度是否与训练一致。
- **代码题 $c$ 怎么数？** 以单元测试 / 官方 checker 为准，不要用 LLM judge 冒充 $c$，否则 $\mathrm{pass@}k$ 量的是「像对」，见 `fund-judge`。
