---
id: openai-loss-spike
section: openai
order: 17
level: S
title: OpenAI：训练 loss 突然炸或变 NaN，怎么分层排查
quick: "我会先保存出问题 step、rank、样本和 RNG，区分有限 spike 与已经污染 Adam 状态的 NaN。再依次查数据、学习率、并行同步和精度；坏 batch 可跳过，脏动量要回干净 checkpoint，不能只降学习率继续跑。"
tags:
  - OpenAI
  - Training
  - Debug
  - NaN
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Mixed Precision Training
    url: https://arxiv.org/abs/1710.03740
    type: primary
  - title: Small-scale proxies for large-scale Transformer training instabilities
    url: https://arxiv.org/abs/2309.14322
    type: primary
  - title: Language Models are Few-Shot Learners
    url: https://arxiv.org/abs/2005.14165
    type: primary
  - title: OpenAI Research Engineer Interview Guide
    url: https://www.tryexponent.com/guides/openai-research-engineer-interview-guide
    type: secondary
---

我会先保留故障现场，判断是可恢复的有限 spike，还是已经让优化器状态变脏的 NaN / Inf。比如 loss 从 2.1 跳到 20 后回来，与 Adam 动量吃进 NaN 后每步都错，需要不同处置。这里按混合精度、Wortsman 的不稳定代理和 GPT-3 的 clip / Adam 公开设定讨论，没有单独候选人报告确认这是一道 OpenAI 原题。

两件事先分开：spike 是有限大数，下一步往往掉回来；NaN / Inf 是非有限值，Adam 的 $m,v$ 一旦吃进去，后面每步都是脏的。前者可以跳过坏 batch；后者通常要回到上一个干净 checkpoint，不能靠再跑一步「很小的 lr」。

## 先复现，再缩小故障范围

打开这次 step 的 rank 日志，不要看平滑后的 dashboard。问四件事：所有 rank 一起炸还是一张卡先 Inf？是第一个 microbatch 还是累加到第 $k$ 个？grad norm 先爆还是 loss 先爆？fp16 的 inf 标志是否亮了（动态缩放见 `nvidia-loss-scale`）。

先 dump 该 step 的 token id，检查数据：是否越出词表、是否整段 ignore index、是否出现超长 HTML / 乱码重复字符把某个 embedding 打满。packing 把两篇文档拼在一起且没文档 mask 时，偶发会出现「目标全是特殊符」的退化序列。标签若是 $-100$ 以外的负数，交叉熵损失（CE） 会在 gather 时读到垃圾。坏 shard 的签名是：复现同一个 data index 必炸，换一条就不炸。

数据排除后对照学习率日程：warmup 还没结束就按大 batch 线性外推后的峰值；cosine 已经到底又被 resume 成初始 lr；或者只对一部分参数组设了 lr。GPT-3 公开用 clip，grad 范数先看一眼：clip 之前已经 Inf，clip 救不了。和 `openai-adamw` 缠在一起的常见误区是：把 $L_2$ 耦合进 Adam 后再把 lr 加大一档，个别坐标步长离谱。

接着对齐各 rank 的行为。一张卡 Inf、其它卡仍 `optimizer.step()`，权重立刻分叉，下一步全员 NaN。Inf 标志必须 all-reduce。Tensor Parallel 漏了一次同步，某一层的 $Q$ 或输出投影只在本地归一，logits 会出现天文数字。Pipeline 跳过某个 microbatch 的梯度同步，表现也像「偶发 spike」。MoE 路由塌缩是另一条，直方图见 `openai-moe-aux-loss`。

精度检查从 fp16 的缩放开始：fp16 没开 loss scale，或 $S$ 太大持续 overflow。bf16 动态范围够，仍可能因为真实发散而 NaN，不要把 bf16 当成「不会炸」。查 inf 要在 unscale 之后、Adam 之前；脏梯度写进动量，后面每步都是 NaN。softmax 漏 $1/\sqrt{d_k}$ 也会在 fp16 里先 Inf，那是实现 bug，见 `openai-softmax-bug`。

处置上，单步 finite 但离谱，就记下 index、skip 再观察。连续多步 skip 或之后仍爬升，说明要继续查 lr、并行或架构，不能都归因于坏样本。Wortsman 那篇把大规模不稳收到小模型上复现，后面才是 qk-norm 一类结构补丁；面试先把数据与同步查完，再谈改模型。

```python
def step_is_poison(loss, params):
    if not torch.isfinite(loss):
        return True
    for p in params:
        if p.grad is not None and not torch.isfinite(p.grad).all():
            return True
    return False
```

skip 只丢当前梯度，权重和 Adam 保留干净状态；NaN 已进入 $m,v$ 就 rewind，即使 lr 乘 $0.1$ 也清不掉脏动量。激活重计算与第一次前向不一致同样是实现 bug，可对照 `openai-grad-checkpoint`。

相关：`openai-transformer-debug`

## 追问

**spike 回来了还要 rewind 吗？**
不必，只要动量没吃 Inf。要记 data index，防止同一条周期性再来。
**怎么证明是数据不是 lr？**
同一 checkpoint、同一 rng，只换那条样本。炸则数据；不炸再查该 step 的 lr / scale / rank 同步。
**grad clip 能当保险丝吗？**
只能压有限大的范数。Inf 进 clip 还是 Inf。clip 之前必须先 `isfinite`。
**bf16 还会 NaN 吗？**
会。范围够只说明不是 fp16 下溢；真实发散、坏数据、漏 all-reduce 照样会破坏 Adam 状态。

## 相关题

- [[sys-loss-spike]]：同一个现象的系统面清单，先查各 rank 这一步的数据、collective 和 skip 决定是否一致，这张偏数值面。
