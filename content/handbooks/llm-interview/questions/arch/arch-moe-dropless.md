---
id: arch-moe-dropless
section: arch
order: 25
level: A
title: Dropless MoE（MegaBlocks）如何避免 token drop？和 capacity padding 差在哪？
quick: "Dropless MoE 不按固定容量 $C$ 截断，每个专家处理路由给它的全部 token，用块稀疏或分组 GEMM 吃下变长的 $n_i$。Capacity padding 则把每个专家补齐到 $C$，形状固定，空位也照样占计算。Dropless 的代价是动态形状难配 CUDA graph，热点专家仍会拉高尾延迟。"
tags:
  - MoE
  - MegaBlocks
  - Dropless
  - Grouped GEMM
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: MegaBlocks
    url: https://arxiv.org/abs/2211.15841
    type: primary
  - title: Switch Transformers
    url: https://arxiv.org/abs/2101.03961
    type: primary
---

MegaBlocks 的 dMoE 让每个专家按实际分到的 token 数 $n_i$ 去算，用 block-sparse 或 grouped GEMM 处理长短不一的专家输入，既不截断到容量 $C$，也不补齐到 $C$。Capacity padding 是按 $C$ 分配、不足的补零：不丢 token，但算力和通信按最坏的 $C$ 付。Dropless 换来的是动态 shape。

这里常有两种误解：一是「没有容量限制所以一定更快」，二是「把 CF 开到很大就是 dropless」。Switch 风格的 MoE 为了静态 buffer，给每个专家一个上限 $C$，超出的 token 直接丢；为了不丢又把 $C$ 开大，就成了按上限 padding，空位照样占显存和通信。MegaBlocks 走的是第三条路。

## 三种实现的形状

记专家 $i$ 实际分到 $n_i$ 个 token，均匀时期望 $n_i\approx kT/N$。

Drop 是 Switch 的做法：只保留 $C$ 个，$n_i\leftarrow\min(n_i,C)$，GEMM 可以按 $C$ 定死。被丢掉的 token 在这一层 MoE 的输出为 $0$（或只剩 residual），质量对 drop 率很敏感，见 `sys-moe-capacity-token-drop`。

Pad to capacity 仍按 $C$ 分配，不足的用零 token 填。没有 drop，但算力和 all-to-all 都按最坏的 $C$ 付，$\mathrm{CF}=1.25$ 就是固定多付 $25\%$。

Dropless / dMoE 让 GEMM 的输入长度就是 $n_i$，不 pad 也不 drop。这需要 grouped GEMM 或 block-sparse 乘法一次把所有专家喂进去，见 `sys-moe-grouped-gemm`。MegaBlocks 把「token 按专家堆叠」看成一块 block-sparse 矩阵乘：行是 token，列块是各专家的 $d_{\mathrm{ff}}$。专家之间没有 dense 的 batched 维，所以不用对齐到同一个 $C$。

## 仍要付的代价

第一笔是动态 shape。$n_i$ 每一步都在变，CUDA graph 会捕获失败或频繁 recapture；EP all-to-all 的 overlap 难做也是同一个根因，见 `sys-moe-alltoall-overlap`。推理时逐 token 生成（decode）更碎，往往要另写 fused kernel，很少直接沿用训练这套 dMoE 图，见 `sys-moe-infer-prefill-decode`。

第二笔是热点依然贵。不 drop 只是不再把质量问题藏成 skip。比如专家 $3$ 拿到 $40\%$ 的 token，那张卡上的 grouped GEMM 和 dispatch 照样决定 P99。Dropless 取消的是静默的质量损失，负载均衡还得做，aux 或 bias 在 dMoE 里照样要，不然实际耗时取决于最慢的专家。

第三笔是显存峰值随 $n_i$ 抖动。按 $C$ 预分配的实现峰值可预测；dropless 按本步最大值分配，极端 batch 可能 OOM。所以工程上还会设一个 soft cap，超过就 drop 或重路由，生产里的「dropless」常常是「几乎 dropless」。

## 怎么选

训练质量优先、能接受动态 kernel，就用 dMoE 加均衡，主要盯 `max n_i`，drop 率退到次要位置。要静态图、编译、推理用 CUDA graph，就回到 capacity，把 CF 和均衡一起调，让 drop $\lt 1\%$。把 CF 开到 $2$ 再说「我们是 dropless」，其实只是在买 padding，跟 MegaBlocks 是两回事。

## 追问

**Dropless 还需要 capacity 这个变量吗？**
作为 soft 上限和显存预算还需要；作为「超出就丢、不进 backward」的硬开关，尽量不用。

**和 expert-choice 是什么关系？**
动机相反。Expert-choice 用固定的 $C$ 从专家那头保证均衡，天然适合 padding，见 `arch-moe-token-vs-expert-choice`。

**反向梯度会有什么变化？**
没有 drop，每个被路由的 token 都会进对应专家的 wgrad。热点专家的梯度范数更大，要配均衡或专家级 lr 缩放，不然这些专家的权重可能先出现不稳定。

**面试怎么收尾？**
Drop 换的是质量，pad 换的是算力，dropless 换的是动态 shape。先说清换掉了什么，再报框架名。
