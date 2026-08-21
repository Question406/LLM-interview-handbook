---
id: arch-moe-dropless
section: arch
order: 25
level: A
title: Dropless MoE（MegaBlocks）如何避免 token drop？和 capacity padding 差在哪？
quick: >-
  不按固定 $C$ 截断，而是让每个专家吃下路由给它的全部 token，用 block-sparse / grouped GEMM 吃变长
  $n_i$。没有「这一层被静默 skip 的 token」，代价是动态 shape、更难 CUDA graph、热点专家仍会拖尾。Capacity
  padding 是另一极端：形状固定但空位白算。
tags:
  - MoE
  - MegaBlocks
  - Dropless
  - Grouped GEMM
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-20
sources:
  - title: MegaBlocks
    url: https://arxiv.org/abs/2211.15841
    type: primary
  - title: Switch Transformers
    url: https://arxiv.org/abs/2101.03961
    type: primary
---

陷阱是把 dropless 说成「没有容量限制所以一定更快」，或说成「和把 CF 开到很大一样」。Switch 风格 MoE 为了静态 buffer，给每个专家一个上限 $C$，多出来的 token **丢掉**；为了不 drop 又把 $C$ 开很大，则按上限 **padding**，空位照样占显存和通信。MegaBlocks 的 dMoE 走第三条路：**ragged 专家规模 + 稀疏/分组 GEMM**，token 按路由结果全算，不补齐到 $C$。

## 三种实现的形状

记专家 $i$ 实际分到 $n_i$ 个 token，均匀时期望 $n_i\approx kT/N$。

1. **Drop（Switch）**：只保留 $C$ 个，$n_i\leftarrow\min(n_i,C)$。GEMM 可以按 $C$ 定死。被丢掉的 token 这一层 MoE 输出为 $0$（或 residual），质量对 drop 率敏感，见 `sys-moe-capacity-token-drop`。
2. **Pad to capacity**：仍按 $C$ 分配，不足的用零 token 填。无 drop，但算力和 all-to-all 按最坏 $C$ 付。$\mathrm{CF}=1.25$ 就是固定多付 $25\%$。
3. **Dropless / dMoE**：GEMM 输入长度就是 $n_i$，不 pad、不 drop。需要 grouped GEMM 或 block-sparse 乘法一次喂进所有专家，见 `sys-moe-grouped-gemm`。

MegaBlocks 把「token 按专家堆叠」看成一块 block-sparse 矩阵乘：行是 token、列块是专家的 $d_{\mathrm{ff}}$。专家之间没有 dense 的 batched 维，所以不必对齐到同一个 $C$。

## 仍要付的代价

**动态 shape。** $n_i$ 每步变，CUDA graph 捕获失败或频繁 recapture；和 EP all-to-all 的 overlap 一样，变长是根因，见 `sys-moe-alltoall-overlap`。推理 decode 更碎，往往另写 fused kernel，而不是训练这套 dMoE 图，见 `sys-moe-infer-prefill-decode`。

**热点仍然贵。** 不 drop 只是不把质量问题藏成 skip：expert $3$ 拿到 $40\%$ token，那张卡的 grouped GEMM 和 dispatch 照样是 P99。Dropless **取消的是静默质量损失**，不是取消负载均衡。Aux / bias 在 dMoE 里照样要，否则墙钟被最慢专家绑死。

**显存峰值随 $n_i$ 抖。** 按 $C$ 预分配的实现峰值可预测；dropless 若按本步最大值分配，极端 batch 可能 OOM。工程上仍会设一个 soft cap：超过则 drop 或重路由，于是「dropless」在生产里常是「几乎 dropless」。

## 怎么选题

训练质量优先、能接受动态 kernel：dMoE + 均衡，盯 `max n_i` 而不是 drop 率。要静态图、编译、推理 CUDA graph：回到 capacity，把 CF 和均衡一起拧，使 drop $\lt 1\%$。把 CF 开到 $2$ 再声称「我们是 dropless」只是在买 padding，不是 MegaBlocks。

## 追问

- **Dropless 还要不要 capacity 这个变量？** 作为 soft 上限和显存预算要；作为「超出即丢、不进 backward」的硬开关尽量不要。
- **和 expert-choice？** Expert-choice 用固定 $C$ 从另一头保证均衡，天然 pad-friendly，和 dMoE 的动机相反，见 `arch-moe-token-vs-expert-choice`。
- **反向梯度？** 没有 drop 则每个被路由的 token 都进对应专家的 wgrad；热点专家梯度范数更大，要配均衡或专家级 lr 缩放，否则那几套权重先炸。
- **面试口诀？** Drop 换质量；pad 换算力；dropless 换动态 shape。先说清换的是什么，再报框架名。
