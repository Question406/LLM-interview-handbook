---
id: arch-moe-gating-softmax-sigmoid
section: arch
order: 22
level: S
title: Mixtral 的 softmax+TopK 和 DeepSeek 的 sigmoid gating 差在哪？gating 何时再归一？
quick: >-
  Mixtral 先对 router logits 取 Top-$k$，再只在选中的 $k$ 个专家上 softmax，gating 和为
  1。DeepSeek-V3 用独立的 sigmoid 亲和度，选专家时加 bias，加权时用不加 bias
  的原分数在选中集合内归一。两者的关键是把「选谁」和「怎么加权」分清楚。
tags:
  - MoE
  - Router
  - Mixtral
  - DeepSeek
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: Mixtral of Experts
    url: 'https://arxiv.org/abs/2401.04088'
    type: primary
  - title: DeepSeek-V3 Technical Report
    url: 'https://arxiv.org/abs/2412.19437'
    type: primary
---

Mixtral 是先截断再归一：对 router logits 取 Top-$k$，只在这 $k$ 个专家上做 softmax，所以 gating 和为 $1$。DeepSeek-V3 用独立的 sigmoid 亲和度，选专家时看加了 bias 的分数，加权时用没加 bias 的原分数在选中集合里归一。写实现时要分清两步：用什么分数做离散选择，用什么分数做加权，这两步可以用不同的表。

最常见的错，是把「softmax 路由」写成先对 $N$ 个专家 softmax、再取 Top-$k$ 当权重。这样 $k$ 个 gating 加起来小于 $1$，没选中的专家还分走了概率质量，combine 相当于给这一层 MoE 乘了一个小于 $1$ 的系数。

## Mixtral：先截断，再在 $k$ 个上 softmax

$N$ 个专家，router $W_g\in\mathbb{R}^{d\times N}$，token 为 $x$：

$$
z=xW_g,\qquad
G(x)=\mathrm{softmax}\bigl(\mathrm{TopK}(z)\bigr),\qquad
y=\sum_{i=1}^{N}G(x)_i\,E_i(x).
$$

$\mathrm{TopK}$ 把没选中的位置打成 $-\infty$（或者先取出 $k$ 维再 softmax），于是只有选中的专家有非零 gating，这 $k$ 个数和为 $1$。$k=2$、$N=8$ 就是 Mixtral-8x7B 的稀疏 FFN：每个 token 激活 $2$ 个 SwiGLU 专家，没有 shared expert，论文也没靠 aux 损失（loss）做均衡。

手写时有两种等价写法：`topk(logits)` 得到 `[T,k]` 再 `softmax(val, dim=-1)`；或者把没选的位置填 `-inf` 再对整行 softmax。对已经 softmax 过的 $N$ 维再取 top-$k$ 当权重，是 Switch 的「选谁」那一步，Mixtral 的「加权」不这么做。

## DeepSeek-V3：sigmoid 亲和，选择和加权拆开

V3 没把 $N$ 个专家当成互斥的类别，亲和度是独立的 sigmoid：

$$
s_{i,t}=\sigma(u_t^\top e_i).
$$

选谁看 $s_{i,t}+b_i$ 的 Top-$k$，其中 $b_i$ 是无辅助负载的 bias，不进 backpropagation。加权时只在选中的 $k$ 个上，用不加 $b_i$ 的 $s_{i,t}$ 归一。所以 bias 只改选中的集合，不改选中之后贡献多大，见 `arch-moe-noaux`。

所以两者的差别在于专家之间是否被当成互斥类别，「一个用 softmax、一个用 sigmoid」只是表面。Softmax 强制 $N$ 个分数抢同一份质量；sigmoid 允许多个专家同时高分，在 $N=256$、$k=8$ 这种细粒度设定下更自然。Shared expert 在这两套 gating 之外常开，不进 Top-$k$，见 `arch-shared-expert`。

## Switch 那条「先 softmax 再 Top-$1$」

Switch 的 $P=\mathrm{softmax}(z)$ 既用来做负载统计，也直接当 gating：$k=1$ 时权重就是 $P_{i^\star}$，故意不把唯一专家的 gating renormalize 成 $1$，路由器没把握时这一层 MoE 的贡献就小一些。Aux 用的也是这张 $P$，见 `code-moe-router-aux-loss`。把这套搬到 Mixtral 的 $k=2$ 上又不做截断后归一，combine 会系统性偏小。

## 追问

**Mixtral 为什么可以不要 aux？**
它粒度粗、$k=2$、专家大，论文观察到负载已经够均匀。细粒度、高稀疏的设定没法照搬，见 `arch-moe-balance`。

**推理时还要噪声或 bias 更新吗？**
不要。训练末期的 router 和冻结的 bias 写进 checkpoint，见 `sys-moe-train-infer-routing-mismatch`。

**$k$ 个 gating 要不要再乘一份完整的 softmax 概率？**
不要叠两套。要么截断后 softmax（Mixtral），要么在选中集合上归一 sigmoid（V3）。

**手写的话测什么？**
随机输入下，Mixtral 路径的 `gates.sum(-1)` 应该全是 $1$；把某个 expert 的 logits 打到极低，它就不该再出现在 `idx` 里。
