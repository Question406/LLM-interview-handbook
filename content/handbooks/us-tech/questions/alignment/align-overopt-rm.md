---
id: align-overopt-rm
section: alignment
order: 28
level: S
title: 对齐：奖励模型过优化——BoN 曲线与代理失效
quick: >-
  proxy RM 分可以一路新高，gold / 人评先升后降。Best-of-N 把 $N$ 加大，和把 RL 步数加大是同一条
  Goodhart 曲线。门禁用另一张 RM 或真任务，不要拿训练 RM 既选模又验收。
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

OpenAI 对齐岗爱问「RM 还在涨，你为什么停」。Gao 等人把这件事画成标量：优化 proxy 奖励时，gold 奖励对「优化程度」先升后降。InstructGPT 已经写过策略会 overoptimize RM。不是某次现场逐字题。具体 hack 样子见 `align-reward-hack`；BoN 作为推理机制见 `align-best-of-n`。本题收**曲线怎么读、代理何时失效**。

## 优化程度当 $x$ 轴，不要当质量

「优化程度」可以是 RL 步数、KL 到参考策略的距离、或 Best-of-N 的 $N$。横轴越大，策略越往 proxy $r_\phi$ 的高分区挤。纵轴画两条：训练 RM（proxy）、held-out RM 或人评（gold）。典型形状：proxy 单调升；gold 有峰值，过了就掉。这就是代理失效——你最大化的量不再跟踪真目标。

BoN 特别好画：同一 $\pi$ 抽 $N$ 条，取 $\arg\max_i r_\phi(x,y_i)$。$N=1$ 是原策略。$\log N$ 增大时 decode 近线性变贵，proxy 分仍涨，gold 会分叉。面试别说「$N$ 是免费质量旋钮」。前缀 KV 能摊 prompt，摊不掉 $N$ 路 decode，见 `align-best-of-n`。

Gold RM 更大、数据更新，峰值往往更晚出现——Gao 的 scaling 叙述。这不是「再训一张更大的 RM 就永远不掉」，只是把拐点推后。用同一张 $r_\phi$ 既选 BoN 又报分，你永远看不见分叉。

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

## 代理失效不只发生在 RL

离线 DPO 也会：优化的是 implicit reward 与偏好数据的一致，held-out 人评仍可掉。Online DPO / 反复用 RM 造 pair，等于把 BoN 写进训练集，污染更狠，见 `align-online-dpo`、`align-eval-contam`。LLM-as-judge 当 gold 只是第二 proxy，位置偏差和家族偏好吃掉拐点，见 `align-llm-judge`。可验证任务用单测当 gold，proxy 可以是格式分——格式新高、单测掉，同一句话。

护栏（面试要落到操作）：

- 训练 RM 不验收。验收用 held-out RM、人抽查、下游任务。
- 对着 gold 曲线早停，或对 KL / $N$ 设硬顶。
- 长度归一再 argmax；BoN 候选里留 SFT 样本，防止完全离开参考文风。
- 定期换 RM 或换切片，防止策略过拟合旧判官。

KL 到参考策略只限制支撑，不告诉你支撑里刷什么，见 `align-rlhf-kl`。所以「KL 还很小」不能当没过优化的证据。

## 追问

- **为什么 proxy 还能涨？** 因为它在被直接最大化。涨只说明优化器工作，不说明产品变好。
- **BoN 和 RL 谁先分叉？** 同一张 RM、同一优化程度度量下形状同类。差在计算发生在推理还是训练。
- **换更大 RM 当 gold 就行了吗？** 能推迟拐点，不能取消 Goodhart。真任务和人抽查仍要在门禁里。
- **RFT 的 grader 会过优化吗？** 会。训练与验收 grader 必须分开，见 `align-rft`。
