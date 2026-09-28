---
id: align-grpo
section: alignment
order: 11
level: S
title: 对齐：GRPO / group relative，相对 PPO 少了 critic
quick: >-
  GRPO 用同一 prompt 下一组样本的奖励均值当 baseline，不再训 value。优势是少一张和策略同量级的 critic；代价是每题必须
  $G>1$，组内奖励全一样时梯度为零。KL 护栏还在，不是「不用 PPO 就不对参考做惩罚」。
tags:
  - OpenAI
  - DeepSeek
  - GRPO
  - RLHF
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: DeepSeekMath — Pushing the Limits of Mathematical Reasoning in Open Language Models
    url: https://arxiv.org/abs/2402.03300
    type: primary
  - title: DeepSeek-R1 — Incentivizing Reasoning Capability in LLMs via Reinforcement Learning
    url: https://arxiv.org/abs/2501.12948
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
---

OpenAI / DeepMind / 做 reasoning post-training 的岗会把 GRPO 当「你是不是真的推过 PPO」。DeepSeekMath 先写出 group relative；R1 把它推到可验证奖励的长推理。别背「没有 critic 所以更稳」。要能说清 baseline 从哪来、$G$ 太小会怎样、和 `align-rlhf-kl` 的反向 KL 还在不在。

## 相对 PPO，少的是哪一块

PPO 的优势函数通常走 GAE：需要 $V_\psi(s)$ 估状态价值。语言建模里「状态」是整段前缀，critic 几乎和策略一样大，还要和策略抢显存、抢同步。GRPO 的做法是：对每个 prompt $x$ 从旧策略采 $G$ 条 $y_1,\ldots,y_G$，打标量奖励 $r_i$，组内标准化

$$
\hat A_i=\frac{r_i-\mathrm{mean}(r)}{\mathrm{std}(r)+\varepsilon}.
$$

同一条序列上每个 response token 共用这个 $\hat A_i$。策略目标仍是 PPO 那套 importance ratio clip，只是 $\hat A$ 不再来自 critic。反向 KL 到 $\pi_{\mathrm{ref}}$ 仍以奖励惩罚或 token 正则出现，见 `align-rlhf-kl`。答成「GRPO 砍掉了 KL」是错的；砍掉的是 learned baseline。

组均值是按 prompt 的控制变量：难题普遍低分、易题普遍高分，减均值之后比的是「这题里谁更好」，不是跨题绝对分。这比全局 moving-average 的 REINFORCE 更贴 LLM 的 prompt 异质性。

```python
def grpo_adv(rewards, eps=1e-6):
    # rewards: [B, G]  scalar per sample
    mu = rewards.mean(dim=-1, keepdim=True)
    std = rewards.std(dim=-1, keepdim=True).clamp_min(eps)
    return (rewards - mu) / std
```

只在 response mask 上乘 $\hat A$ 再反传。Prompt token 进策略梯度，等于把「读懂题」当动作。

## $G$、方差、全对/全错

没有 critic 不是免费午餐。$G=1$ 时标准差没定义，组相对无从谈起。$G$ 很小（2、4）且奖励很稀疏（数学对错 0/1），一个组经常全 0 或全 1，$\hat A=0$，这批零学习。工程上要：足够 $G$（常见 8 到 16）、温度别榨干多样性、可验证任务混一点能拉开的题。过程监督想密化奖励，见 `align-process-reward`，和 GRPO 正交：PRM 改 $r$，不替代组 baseline。

clip 仍然相对 $\pi_{\mathrm{old}}$，不是相对 $\pi_{\mathrm{ref}}$。两个参照别混：old 管单步别跳；ref 管别离开可用语言。ratio 在序列级还是 token 级平均，会改有效步长，换实现先对齐这一项。

奖励被刷的方式和 PPO 相同。规则奖励会 hack 格式、空实现、把答案写进打印；学到的 RM 会冗长和套话，见 `align-reward-hack`。GRPO 不会自动免疫 Goodhart，只是少训一张会过拟合的 $V$。

## 面试怎么收

资源紧、奖励可验证（数学、代码、单测）：GRPO 合理，省一张 critic，数据闭环也简单。开放对话、奖励噪声大、组内分不开：组标准化会放大标注噪声，PPO + 学到的 $V$ 或先训 RM 再 RL 更常见。和 DPO 比：DPO 离线、不 rollout，见 `align-dpo`；GRPO 在线、要采样。不是「R1 证明 DPO 过时了」。

我会画：$G$ 条柱子、均值当零轴、clip 盒子、旁边再画一个没画出来的 critic。评委要听的是你知道省了什么计算、引入了什么方差。

## 追问

- **组标准化和减一个全局 baseline 有何不同？** 全局 baseline 不消 prompt 难度；组内均值把「题难」和「这题答得好」拆开。
- **全对的组怎么办？** 优势为零。换温度、加题、或混 outcome 与过程信号，不要只加大 LR 硬冲。
- **还要 value 头吗？** 默认不要。若 $G$ 上不去又要稳，再讨论 critic，那就是回到 PPO 族。
- **和 Best-of-N 是一回事吗？** 不是。BoN 是推理时用 RM 挑一条，见 `align-best-of-n`；GRPO 用组统计更新权重。
