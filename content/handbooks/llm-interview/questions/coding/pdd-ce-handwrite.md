---
id: pdd-ce-handwrite
section: coding
order: 181
level: A
title: 拼多多应用开发：如何手写交叉熵，数值上要防什么？
quick: "对 logits 做 log-softmax 再按目标 token gather 取负。禁止先 softmax 再 $\\log$，会下溢。实现上用 `logsumexp` 或 `log_softmax`，padding 位置 mask 掉再按有效 token 平均。"
tags:
  - PDD
  - Cross Entropy
  - Coding
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 拼多多大模型应用开发一面凉经
    url: https://www.nowcoder.com/feed/main/detail/f87fcee060ea404ba99a20245f746e60
    type: candidate-first-hand
---

## 真题记录

- 公司：拼多多
- 团队 / 岗位：大模型应用开发
- 届别 / 流程：一面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“手写交叉熵”**

常见误区是：先 `softmax` 再 `log`：概率下溢成 0，$log0\to-\infty$。必须 log 域：减行最大值再 `logsumexp`。同面 Attention 见 `pdd-attention-handwrite`。序列任务还要用 `ignore_index` 丢掉 pad，见 `baidu-qwen2-sft-implementation`。

## 公式：NLL = $-z_y + \mathrm{logsumexp}(z)$

对 logits $z\in\mathbb{R}^{V}$ 与类别 $y$：

$$
\ell=-z_y+\mathrm{logsumexp}(z),\qquad
\mathrm{logsumexp}(z)=\max_j z_j+\log\sum_j e^{z_j-\max z}.
$$

减 max 不改变 softmax，但让指数落在 $(0,1]$。label smoothing 时目标不再 one-hot，变成对平滑分布的交叉熵。均匀初始化时 $\ell\approx\log V$：十万词表约 $11.5$，用来判断初始 loss 是否离谱。

```python
import torch

def cross_entropy(logits, target, ignore_index=-100):
    # logits: [N, V], target: [N]
    z = logits - logits.max(dim=-1, keepdim=True).values
    logp = z - z.exp().sum(dim=-1, keepdim=True).log()
    safe = target.clamp(min=0)
    nll = -logp.gather(1, safe.unsqueeze(1)).squeeze(1)
    mask = target != ignore_index
    return nll[mask].mean()
```

`gather` 前把 ignore 位置 clamp 是为了不越界，真正平均只在 `mask` 上。不要对 pad 位置算完再乘 0 却仍除以 $N$（分母应是有效 token 数）。

## 序列 LM：shift 与平均方式

Causal LM 用 `logits[:, :-1]` 对 `labels[:, 1:]`。HF 的 `labels=` 已内部 shift；手写时只做一次。平均可以按 token 或按序列：长句会主导 token 平均；GRPO/SFT 论文对「按序列还是按 token」很敏感，见 `baidu-grpo-loss-agg`。面试先写 token 平均 + ignore pad，再口头说另一种。

fp16 下 `exp` 仍可能溢，max 之后通常安全；极端值可升 fp32。禁止 `F.softmax` 再 `log`。

## 追问

- **起步 loss 多少算正常？** 均匀约 $\log V$。7 万词表 $\approx 11.2$。若一开始是 0.1，多半 label 全是 ignore 或 logits 泄漏了答案。
- **为什么 clamp target？** ignore 下标不能进 `gather`；clamp 后靠 mask 丢掉这些 NLL。
- **label smoothing？** $q=(1-\varepsilon)e_y+\varepsilon/V$，loss 是 $-q\cdot\log\pi$，不是只取 $y$ 一列。
- **和 KL？** 对 one-hot 的交叉熵损失（CE） 等于相对均匀基线的 KL 差一个常数。平滑后是对 $q$ 的 CE。
- **分母用 batch 还是有效 token？** 必须有效 token。pad 多的 batch 否则 loss 被人为缩小。
