---
id: sys-moe-grouped-gemm
section: systems
order: 36
level: S
title: MoE 专家计算为什么要用 Grouped GEMM，而不是 for-loop 或 pad 成 batched GEMM？
quick: >-
  各专家的 token 数 $n_i$ 不同。For-loop 每次 kernel 启动太碎；按 $\max n_i$ 或 capacity
  $C$ padding 会白算空位。Grouped GEMM 一次 kernel 吃进一组变长 $(n_i,d,d_{\mathrm{ff}})$，把稀疏
  MoE 重新变成高占用矩阵乘。负载不均时它救不了最慢专家，只救启动开销和 padding。
tags:
  - MoE
  - Grouped GEMM
  - Systems
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: MegaBlocks
    url: https://arxiv.org/abs/2211.15841
    type: primary
  - title: DeepSeek-V3 Technical Report
    url: https://arxiv.org/abs/2412.19437
    type: primary
---

这块容易把 MoE 前向画成「$N$ 个 `nn.Linear` 循环」。白板能过，上卡就死在 kernel launch 和空算。Permute 之后每个专家拿到一段连续 token，真正贵的是 **怎么喂进 Tensor Core**。三种喂法对应三种浪费。

## 三种算子

Permute 之后专家 $i$ 的输入是 $X_i\in\mathbb{R}^{n_i\times d}$，权重 $W_i\in\mathbb{R}^{d\times d_{\mathrm{ff}}}$（SwiGLU 再乘一门一升）。$n_i$ 随路由变。

1. **For-loop。** `for i in experts: Y_i = X_i @ W_i`。$n_i=0$ 的专家可跳，但 $N=64$ 或 $256$ 时启动次数按专家数涨。Decode 或小微批时 $n_i$ 只有几个 token，GEMM 本身几微秒，启动和同步变成主因。
2. **Pad + batched GEMM。** 把每个 $X_i$ 补到 $C$ 或 $\max_i n_i$，堆成 `[N, C, d]`，一次 `bmm`。Shape 静态、好写 CUDA graph，但空位按 dense 算。$\mathrm{CF}=1.25$ 且负载再歪一点，有效 FLOPs 占比会掉到 $50\%$ 以下。这是 capacity padding 的算子面，见 `arch-moe-dropless`、`sys-moe-capacity-token-drop`。
3. **Grouped GEMM。** 一次 kernel 接收 $N$ 组不同的 $(m_i,n,k)=(n_i,d_{\mathrm{ff}},d)$，组间不要求 $m_i$ 相同。无 padding，启动一次。MegaBlocks / Transformer Engine / CUTLASS grouped GEMM 都是这条。Dropless 训练几乎必须靠它，否则变长 $n_i$ 只能退回循环。

我会把 grouped GEMM 说成「batched GEMM 的变长版」：batched 要求每组 $m$ 相同；grouped 允许每组 $m$ 不同。不要背具体 API。

## 什么时候 grouped 也不够

**热点专家。** Grouped kernel 内部仍要等最大的那块 $n_i$。Overlap 藏的是平均通信，藏不住 P99，见 `sys-moe-alltoall-overlap`。先均衡，再换算子。

**太小的 $n_i$。** 即使合成一次 launch，$n_i=1$ 的组仍吃不满 Tensor Core。Decode 要走 fused MoE（把 router、gather、多专家 MLP 写进一个 kernel），而不是训练用的 grouped GEMM，见 `sys-moe-infer-prefill-decode`。

**权重布局。** 专家权重按 `[N, d, d_ff]` 连续存放，grouped kernel 才能按组指到 $W_i$。EP 之后每卡只有 $N/\mathrm{EP}$ 个专家，grouped 的组数是本地专家数，不是全局 $N$，见 `sys-expert-parallel`。Shared expert 每 token 都走，通常单独一条 dense GEMM，不要塞进 routed 的 grouped 调用。

## 怎么选

Prefill / 训练微批足够大：$n_i$ 上百，grouped GEMM 是默认。Shape 必须静态、且均衡已经很好：pad 到 $C$ 换 graph。专家极多、单专家极小：先怀疑细粒度切分过碎，再堆 kernel。评测看 SM 利用率、padding 浪费比例、kernel 次数，不要只报 MFU。MFU 会被 padding 虚高。

## 追问

- **和 `torch.bmm` 差在哪？** `bmm` 要同一 $m$；grouped 要一份 `m_sizes`。把 `n_i` 不同的专家 `stack` 起来再 `bmm` 就是偷偷 padding。
- **反向？** 每个专家一份 dgrad / wgrad，同样变长，也要 grouped。只融合前向、反向走 Python 循环，训练会在后向爆。
- **$n_i=0$？** 该组跳过，不要丢一个 $0\times d$ 进 kernel。Counts 用 `bincount` 得到，见 `code-moe-permute-combine`。
- **和 EP all-to-all 谁先谁后？** 先 dispatch 到持有该专家的卡，再本地 grouped GEMM，再 combine。Grouped 不替代通信。
