---
id: align-overopt-rm
section: alignment
order: 28
level: S
title: 对齐：奖励模型过优化——BoN 曲线与代理失效
quick: "优化奖励模型时，我会同时看训练奖励和独立人评或任务得分。训练奖励继续升、独立得分开始掉，就到了过优化阶段；这时按独立得分早停，并限制 KL 或 Best-of-N 的候选数。"
tags:
  - OpenAI
  - Reward Model
  - Best-of-N
  - RLHF
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Scaling Laws for Reward Model Overoptimization
    url: https://arxiv.org/abs/2210.10760
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
  - title: Direct Preference Optimization
    url: https://arxiv.org/abs/2305.18290
    type: primary
---

训练奖励继续涨也可能需要停，因为策略学到的可能是奖励模型的漏洞。判断时我会把训练 RM 当 proxy，另用独立 RM、人评或任务结果作为 gold，同时画两条曲线。Gao 等人的实验展示了 gold 先升后降的现象，InstructGPT 也记录过对奖励模型（RM）的过优化。

## 两条曲线怎么读

把优化程度放在 $x$ 轴，它可以是 强化学习（RL） 步数、KL 到参考策略的距离、或 Best-of-N 的 $N$。横轴越大，策略越往 proxy $r_\phi$ 的高分区挤。纵轴画两条：训练 RM（proxy）、held-out RM 或人评（gold）。典型形状：proxy 单调升；gold 有峰值，过了就掉。这就是代理失效：你最大化的量不再跟踪真目标。

BoN 特别好画：同一 $\pi$ 抽 $N$ 条，取 $\arg\max_i r_\phi(x,y_i)$。$N=1$ 是原策略。$\log N$ 增大时 逐 token 生成（decode） 近线性变贵，proxy 分仍涨，gold 会分叉。候选数 $N$ 增大也会增加成本。前缀 KV 可以复用处理输入的计算，但无法省去 $N$ 路回答生成，见 `align-best-of-n`。

Gold RM 更大、数据更新，峰值往往更晚出现（Gao 的 scaling 叙述）。更大的 RM 可以推迟拐点，但无法保证拐点消失。用同一张 $r_\phi$ 既选 BoN 又报分，你永远看不见分叉。

```python
def bon_curve(scores_proxy, scores_gold):
    # scores_*: [B, N]  已按 proxy 排序的候选
    # 看 k=1..N 时 proxy 均值 vs gold 均值
    best_p = scores_proxy.cummax(dim=-1).values.mean(dim=0)
    idx = scores_proxy.argmax(dim=-1, keepdim=True)
    # gold 必须用「proxy 选中的那条」再平均，不能对 gold 自己再 argmax
    return best_p
```

长度几乎一定参与分叉：更长更容易撞上 RM 喜欢的 n-gram，见 `align-length-bias`。先画长度 vs proxy 散点，再叠 gold。

## 怎么发现并限制过优化

离线 直接偏好优化（DPO） 也会：优化的是 implicit 奖励分数（reward） 与偏好数据的一致，held-out 人评仍可掉。Online DPO / 反复用 RM 造 pair，等于把 BoN 写进训练集，污染风险更高，见 `align-online-dpo`、`align-eval-contam`。LLM-as-judge 当 gold 只是第二 proxy，位置偏差和家族偏好可能掩盖拐点，见 `align-llm-judge`。可验证任务用单测当 gold，proxy 可以是格式分：格式新高、单测掉，同一句话。

我会用 held-out RM、人工抽查和下游任务验收，根据 gold 曲线早停，并给 KL 或 $N$ 设上限。BoN 选答案时先做长度归一，再 argmax，候选里留一些监督微调（SFT）样本，避免完全离开参考文风。评测还要定期换 RM 或切片，检查策略有没有过拟合旧裁判。

KL 到参考策略的约束只限制策略偏离的程度，不能保证策略不会利用奖励模型的偏差，见 `align-rlhf-kl`。所以「KL 还很小」不能当没过优化的证据。

## 追问

**为什么 proxy 还能涨？**
因为它在被直接最大化。涨只说明优化器工作，不说明产品变好。
**BoN 和 RL 谁先分叉？**
同一张 RM、同一优化程度度量下形状同类。差在计算发生在推理还是训练。
**换更大 RM 当 gold 就行了吗？**
能推迟拐点，不能取消 Goodhart。真任务和人抽查仍要在门禁里。
**RFT 的 grader 会过优化吗？**
会。训练与验收 grader 必须分开，见 `align-rft`。

相关：`align-reward-hack`。

## 相关题

- [[align-best-of-n]]：同一条曲线从推理侧问，重点是 BoN 的生成成本和 $N$ 该开多大。
- [[align-reward-hack]]：这张讲曲线为什么会分叉，那张举冗长、谄媚、格式刷分的具体例子，并讲训练中怎么发现。
- [[align-reward-model]]：过优化的源头是 RM 本身的噪声和偏好，那张讲 RM 怎么训、怎么校准。
