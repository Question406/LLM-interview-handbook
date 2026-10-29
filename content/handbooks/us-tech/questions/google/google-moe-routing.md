---
id: google-moe-routing
section: google
order: 16
level: S
title: Google：MoE 路由、容量因子和 decode 专家并行怎么落地
quick: >-
  MoE 先用路由器选 top-$k$ 专家，再把 token 按专家重排、补齐到容量 $C$，批量计算后还原顺序；超过容量的 token
  按策略丢弃。Decode 每步 token 少，all-to-all 容易受小消息延迟限制，因此常需降低 EP 度或复制热点专家，同时保持路由权重一致。
tags:
  - Google
  - MoE
  - Routing
  - TPU
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: >-
      Switch Transformers — Scaling to Trillion Parameter Models with Simple and
      Efficient Sparsity
    url: 'https://arxiv.org/abs/2101.03961'
    type: primary
  - title: >-
      GShard — Scaling Giant Models with Conditional Computation and Automatic
      Sharding
    url: 'https://arxiv.org/abs/2006.16668'
    type: primary
  - title: ST-MoE — Designing Stable and Transferable Sparse Expert Models
    url: 'https://arxiv.org/abs/2202.08906'
    type: primary
  - title: Gemini 1.5 Technical Report
    url: 'https://arxiv.org/abs/2403.05530'
    type: primary
---

## 可以这样回答

MoE 路由落到实现上，就是把 token 按专家重排，补齐到静态容量，再批量计算并还原顺序。比如一批 token 大多选中同一个专家，这个专家会先满，其他专家却可能空着，通信和计算都得等它。TPU 的 XLA 还要求静态 shape，动态路由因此要付出 padding 和重排成本。总体机制见 `google-gemini-moe`，mesh 轴见 `google-tpu-mesh`，SPMD 见 `google-jax-pjit`。

MoE 层输入 $x$ 为 $[n, D]$，$n\approx B\cdot T$。路由器是一条线性：$g=\mathrm{softmax}(x W_r)$，$W_r$ 形状 $[D, E]$，$g$ 形状 $[n, E]$。取每行 top-$k$ 的专家编号和 gating weights。Switch 用 $k=1$，dispatch 简单；GShard 常用 $k=2$，第二个专家当残差备份。Gemini 具体 $E,k$ 没公开，现场用 Switch 的语言讲，不要编超参。

## 技术备查

MoE 路由落到实现上，就是把 token 按专家重排，补齐到静态容量，再批量计算并还原顺序。比如一批 token 大多选中同一个专家，这个专家会先满，其他专家却可能空着，通信和计算都得等它。TPU 的 XLA 还要求静态 shape，动态路由因此要付出 padding 和重排成本。总体机制见 `google-gemini-moe`，mesh 轴见 `google-tpu-mesh`，SPMD 见 `google-jax-pjit`。

MoE 层输入 $x$ 为 $[n, D]$，$n\approx B\cdot T$。路由器是一条线性：$g=\mathrm{softmax}(x W_r)$，$W_r$ 形状 $[D, E]$，$g$ 形状 $[n, E]$。取每行 top-$k$ 的专家编号和 gating weights。Switch 用 $k=1$，dispatch 简单；GShard 常用 $k=2$，第二个专家当残差备份。Gemini 具体 $E,k$ 没公开，现场用 Switch 的语言讲，不要编超参。

为了让 TPU 批量执行规整 GEMM，可以按下面的顺序处理：

1. 根据专家 id 把 token permute 成「专家 0 的一段、专家 1 的一段、…」。
2. 每段 pad 到容量 $C$，得到大约 $[E, C, D]$（或按 EP 切成每芯一块）。
3. 各专家一次 batched GEMM。
4. 按逆 permute combine，用 gating weights 加权，写回原顺序 $[n, D]$。

路由器本身是小矩阵，不是瓶颈。瓶颈是 permute 的不规则 gather、padding 浪费的 FLOPs、以及后面的 all-to-all。

负载均衡 auxiliary loss（Switch）：

$$
\mathcal{L}_{\mathrm{aux}} = \alpha\, E \sum_{i=1}^{E} f_i P_i
$$

$f_i$ 是实际派到专家 $i$ 的 token 比例，$P_i$ 是路由器给它的平均概率。两者都均匀时最小。ST-MoE 再加 router z-loss，惩罚过大的 logits，训练更稳。均衡负载也有系统收益：减少某个专家过载，降低后面 all-to-all 的 P99。

$$
C=\left\lceil \gamma\cdot n / E\right\rceil
$$

$\gamma$ 常见 $1.0$：$1.25$。专家 $i$ 只收 $C$ 个槽。分数低的 token drop：这层 FFN 输出走残差或零。$\gamma$ 太小，质量掉；太大，padding 和通信体积涨，稀疏红利没了。

TPU 上 $C$ 必须是编译期上界。真实直方图每步都变，你仍按 $C$ pad。平均利用率在 $1/\gamma$ 以下，MXU 在算零。这就是「稀疏理论 FLOPs」和实际耗时对不上的主要来源之一，和 `google-tpu-llm` 的 MXU 利用率是同一笔账。

Drop 的梯度：被丢掉的 token 这层没有专家梯度，路由器仍可能收到「你把我分到满员专家」的信号，取决于实现。面试说清「我假设 drop 后走残差、aux loss 仍按 dispatch 计数」即可，不要现场发明 Gemini 的 kernel。

All-to-all 形状：EP 把 $E$ 个专家铺到芯片上，每芯存 $E/\mathrm{EP}$ 份权重。Dispatch 把 token 按目的 rank 搬走，消息长度随负载变，不是 dense all-reduce 那种固定 $[D]$。尾延迟由收 token 最多的那张卡决定。

Prefill / 训练：$n$ 大，all-to-all 有体积，还能和计算重叠（要切微批，同批 dispatch 叠不上该批 GEMM）。

Decode：每步 $T=1$，$n$ 等于并发请求数。若 $B=16$、$E=64$、$k=2$，大多数专家这步是空的，少数专家挤一堆。此时：

- $C$ 按公式会小到没意义，实现会设最小容量，或改成「被点名才 launch」。
- All-to-all 变成短消息，主要受固定延迟限制。
- 单 token 可能跨芯片取专家，比稠密 FFN 更慢。

所以 serving 常常降低 EP 度、复制热专家、输入 prefill 和 decode 用不同拓扑。训练图原样搬来 decode，是常见错法。路由权重本身必须和训练一致，改的是并行，不是 router。

分组 GEMM、把空专家 skip 掉，能救 GPU；TPU 更爱 pad 成规整块，空槽照算。这里要根据硬件分别分析。MXU 为什么讨厌瘦矩阵，见 `google-tpu-llm`。

## 追问

**$k=2$ 的第二个专家一定算吗？**
GShard 可以：主专家满了再溢出。容量策略和 $k$ 是两件事，别绑死。

**为什么训练和推理不能各用一套 router？**
负载统计会漂，质量对不齐。Serving 可以改 EP / 复制，不该偷偷改 gating。

**共享专家干什么？**
所有 token 都过的稠密 FFN，给路由器减负。公开 Gemini 没写成必选项，当工程开关。

**aux loss 权重 $\alpha$ 怎么调？**
先看专家直方图和 drop 率，再看下游。$\alpha$ 太大，路由变均匀但任务专家化被压死；太小，塌缩成几个稠密 FFN。

## 相关题

- [[google-gemini-moe]]：同为 Google 的 MoE 题，和本题高度重合；那题偏口答产品直觉，讲稀疏为什么不让 decode 便宜 $E$ 倍。
- [[openai-moe-aux-loss]]：本题追问 $\alpha$ 怎么调的展开，aux loss 的公式和塌缩的监控指标。
- [[nvidia-fused-moe]]：本题路由一步里的 permute 落到 kernel 上，讲 grouped GEMM 和 unpermute 怎么融合。
- [[sys-ep-dispatch]]：decode 专家并行的 dispatch 负载，一步耗时由收 token 最多的卡决定，以及 EPLB 复制热专家。
- [[xai-grok-moe]]：同样讲 prefill 和 decode 应该用不同 EP 宽度，以 Grok-1 为例。
