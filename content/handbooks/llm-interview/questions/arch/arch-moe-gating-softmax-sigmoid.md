---
id: arch-moe-gating-softmax-sigmoid
section: arch
order: 22
level: S
title: Mixtral 的 softmax+TopK 和 DeepSeek 的 sigmoid 门控差在哪？门控何时再归一？
quick: "Mixtral 先对 router logits 取 Top-$k$，再只在选中专家上 softmax。DeepSeek-V3 用 sigmoid 亲和度，选专家时加 bias，加权时用原分数在选中集合内归一。"
tags:
  - MoE
  - Router
  - Mixtral
  - DeepSeek
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Mixtral of Experts
    url: https://arxiv.org/abs/2401.04088
    type: primary
  - title: DeepSeek-V3 Technical Report
    url: https://arxiv.org/abs/2412.19437
    type: primary
---

常见误区是：把「softmax 路由」写成先对 $N$ 个专家 softmax、再取 Top-$k$ 当权重。那 $k$ 个门控之和小于 $1$，未选中专家仍分走了概率质量，combine 等于把一层 MoE 乘了一个小于 $1$ 的系数。实现上要分清：用什么分数做离散选择，用什么分数做加权，这两步可以不是同一张表。

## Mixtral：先截断，再在 $k$ 个上 softmax

$N$ 个专家，router $W_g\in\mathbb{R}^{d\times N}$，文本处理单位（token） $x$：

$$
z=xW_g,\qquad
G(x)=\mathrm{softmax}\bigl(\mathrm{TopK}(z)\bigr),\qquad
y=\sum_{i=1}^{N}G(x)_i\,E_i(x).
$$

$\mathrm{TopK}$ 把未选中位置打成 $-\infty$（或先取出 $k$ 维再 softmax）。于是只有选中专家有非零门控，且这 $k$ 个数和为 $1$。$k=2$、$N=8$ 时就是 Mixtral-8x7B 的稀疏 FFN：每 token 激活 $2$ 个 SwiGLU 专家，没有 shared expert，论文也不靠 aux 损失（loss） 做均衡。

手写时常见两种等价实现：`topk(logits)` 得到 `[T,k]` 再 `softmax(val, dim=-1)`；或把未选位置填 `-inf` 后对整行 softmax。不要对已经 softmax 过的 $N$ 维再 top-$k$ 当权重，那是 Switch 的「选谁」步骤，不是 Mixtral 的「加权」步骤。

## DeepSeek-V3：sigmoid 亲和，选择和加权拆开

V3 不用「$N$ 类互斥概率」。亲和是独立的 sigmoid：

$$
s_{i,t}=\sigma(u_t^\top e_i).
$$

选谁：看 $s_{i,t}+b_i$ 的 Top-$k$（$b_i$ 是无辅助负载的 bias，不进反传）。加权：只在选中的 $k$ 个上用未加 $b_i$ 的 $s_{i,t}$ 归一。Bias 只改集合，不改「选中之后贡献多大」，见 `arch-moe-noaux`。

和 Mixtral 的差别不在「一个用 softmax、一个用 sigmoid」这句口号，而在专家之间是否被当成互斥类别。Softmax 强制 $N$ 个分数抢同一份质量；sigmoid 允许多个专家同时高分，细粒度 $N=256$、$k=8$ 时更自然。Shared expert 在这两套门控之外常开，不进 Top-$k$，见 `arch-shared-expert`。

## Switch 那条「先 softmax 再 Top-$1$」

Switch 的 $P=\mathrm{softmax}(z)$ 既做负载统计又做门控：$k=1$ 时权重就是 $P_{i^\star}$，故意不把唯一专家的门控 renormalize 成 $1$，路由器低置信时这一层 MoE 贡献变小。Aux 用的也是这张 $P$，见 `code-moe-router-aux-loss`。把它抄到 Mixtral 的 $k=2$ 上还不做截断后归一，combine 会系统性偏小。

## 追问

- **为什么 Mixtral 可以没有 aux？** 粗粒度、$k=2$、专家大，论文观察到负载够均。细粒度高稀疏不能照抄，见 `arch-moe-balance`。
- **推理还要不要噪声 / bias 更新？** 不要。训练末期的 router 和冻结 bias 写进 checkpoint，见 `sys-moe-train-infer-routing-mismatch`。
- **$k$ 个门控要不要再乘一份完整 softmax 概率？** 不要叠两套。要么截断后 softmax（Mixtral），要么选中集合上归一 sigmoid（V3）。
- **手写测什么？** 随机输入下 Mixtral 路径 `gates.sum(-1)` 应全是 $1$；把某 expert logits 打到极低，它不应再出现在 `idx` 里。
