---
id: align-grpo
section: alignment
order: 11
level: S
title: 对齐：GRPO / group relative，相对 PPO 少了 critic
quick: "GRPO 对同一输入采样一组回答，用组内奖励均值与标准差构造优势，省去单独训练 value critic。代价是每题要有 $G>1$ 个样本，奖励全一样就没有相对学习信号；它仍保留 PPO 式 clip 和参考策略 KL。"
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

GRPO 用同一道题里一组回答的奖励作比较，替代 PPO 中学习出来的 value baseline，因此省下一张与策略规模接近的 critic。比如数学题的一组回答里有对有错，就可以鼓励高于组均值的回答；全部答错则无从比较。

PPO 通常用 $V_\psi(s)$ 和 GAE 估优势，语言模型的状态是一整段前缀，critic 会占用大量显存与同步资源。GRPO 对每个 prompt $x$ 从旧策略采 $G$ 条 $y_1,\ldots,y_G$，得到标量奖励 $r_i$，然后算：

$$
\hat A_i=\frac{r_i-\mathrm{mean}(r)}{\mathrm{std}(r)+\varepsilon}.
$$

同一回答的每个 response token 共享优势 $\hat A$，也就是这里的 $\hat A_i$，只在 response mask 内反传，prompt 不作为动作。组均值减去题目本身的难度，比全局 moving-average REINFORCE 更贴近不同 prompt 的差异。策略目标仍使用 PPO 的 importance ratio clip，反向 KL 到 $\pi_{\mathrm{ref}}$ 也仍可作为奖励惩罚或 token 正则，见 `align-rlhf-kl`。

```python
def grpo_adv(rewards, eps=1e-6):
    # rewards: [B, G]  scalar per sample
    mu = rewards.mean(dim=-1, keepdim=True)
    std = rewards.std(dim=-1, keepdim=True).clamp_min(eps)
    return (rewards - mu) / std
```

## 采样成本与零信号组

省 critic 的代价是多采样。$G=1$ 时标准差没定义；$G$ 很小，如 2、4，数学 0/1 奖励很容易整组全 0 或全 1，$\hat A=0$。可以增加 $G$，常见 8 到 16，保留采样温度带来的多样性，并混入当前模型能分出对错的题。加大 LR 无法修复零优势。PRM 可让 $r$ 更密，但并不替代组 baseline，见 `align-process-reward`。

Clip 比较的是 $\pi_{\mathrm{old}}$，限制单次更新幅度；参考 $\pi_{\mathrm{ref}}$ 用来约束长期偏移。Ratio 按序列还是按 token 平均，会改变有效步长，换实现要先对齐。规则奖励仍可能被格式、空实现、答案打印利用，学到的 RM 仍可能偏冗长套话，见 `align-reward-hack`，少一张 $V$ 并不消除 Goodhart。

DeepSeekMath 提出 group relative，R1 将它用于可验证奖励的长推理。资源紧且数学、代码、单测奖励可靠时，这条路线很合适；开放对话奖励噪声大、组内分不出时，标准化会放大标注噪声，可以考虑 PPO 加学到的 $V$，或先训 RM 再 RL。DPO 是离线偏好更新，无需 rollout；GRPO 在线采样再更新，见 `align-dpo`。这也是 OpenAI / DeepMind 等 reasoning post-training 讨论里常比较的取舍。

## 追问

**组 baseline 比全局 baseline 多做了什么？**
它先扣掉当前题的平均难度，比较同一道题内谁更好。

**全对的组怎么办？**
优势为零，可以换温度、换题或混 outcome 与过程信号，不能只提高 LR。

**还需要 value 头吗？**
默认不需要。如果 $G$ 上不去且需要更稳定的估计，再考虑 critic，就回到 PPO 家族。

**和 Best-of-N 一样吗？**
不同。BoN 用 RM 从 $N$ 个候选挑一条，见 `align-best-of-n`，GRPO 用组统计更新策略权重。

## 相关题

- [[coding-rloo-advantage]]：leave-one-out baseline，与 GRPO 差 $\frac{G}{G-1}$ 倍及除 std。
- [[sys-group-size]]：$G$ 的显存与方差，以及 $G>1$ 的要求。
- [[sys-adv-bcast]]：序列优势广播到 token，prompt 与 pad 置 0。
- [[sys-kl-place]]：KL 在 reward 或 loss 中的梯度路径。
- [[anthropic-grpo-debug]]：零方差组的调试。
- [[align-best-of-n]]：推理选样本与训练更新的区别。
