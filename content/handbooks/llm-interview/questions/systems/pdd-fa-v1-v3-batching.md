---
id: pdd-fa-v1-v3-batching
section: systems
order: 182
level: S
title: 拼多多推理岗：FlashAttention V1–V3 差在哪，什么是 Dynamic Batching？
quick: >-
  三代都在减 HBM I/O：V1 分块 + online softmax；V2 提高并行、少 kernel、更好的 warp
  均衡；V3 利用新硬件的异步执行和低精度计算。Dynamic / continuous batching
  在 iteration 级插入或踢出请求，避免静态 batch 必须等待最长序列。
tags:
  - PDD
  - FlashAttention
  - Inference
  - Dynamic Batching
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 拼多多 大模型推理岗 时间线
    url: https://www.nowcoder.com/feed/main/detail/64c50862afd74ba0b9d8209b3e07571f
    type: candidate-first-hand
  - title: FlashAttention
    url: https://arxiv.org/abs/2205.14135
    type: primary
  - title: FlashAttention-2
    url: https://arxiv.org/abs/2307.08691
    type: primary
  - title: FlashAttention-3
    url: https://arxiv.org/abs/2407.08608
    type: primary
---

## 真题记录

- 公司：拼多多
- 团队 / 岗位：搜推部门大模型推理（候选人由服务端转入）
- 届别 / 流程：一面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“FlashAttention原理，Online softmax，有没有看过cuda kernel，FlashAttention V1,V2,V3，FlashDecoding原理”**；**“有没有听说过Dynamic Batching”**

常见误区是：把 FA 说成「更快的 matmul」，或把 Dynamic Batching 说成「把请求攒成更大的静态 batch」。FA 三代都在减 HBM I/O：标准注意力要物化 $N\times N$ 的 $S$ 和 $P$，带宽打满、显存 $O(N^2)$。FA 把 $Q,K,V$ 分块进 SRAM，用 online softmax 在块间维护行 max 与 sum，不物化整幅矩阵。Dynamic / continuous batching 解决的是 调度：iteration 级插入或踢出请求，避免静态 batch 必须等待最长序列。两者一层算子、一层 serving，不要并成一个词。同面 reduce / warp shuffle 是 CUDA 基本功，要能画 shared memory。

## V1 到 V3 与 FlashDecoding

V1：tiling + online softmax。每块算局部 $m_i$、$ \ell_i$，按下式归并：新 max $m=\max(m_{\mathrm{old}},m_{\mathrm{blk}})$，再 rescale 旧分子分母。数值稳定且 $O(N)$ 额外 SRAM 状态。V2：序列维更并行（一 warp 处理更多行）、减少 kernel launch、更好的 occupancy 与 warp 负载均衡，训练吞吐明显提高。V3：针对 Hopper 一类异步 TMA / WGMMA 与低精度 GEMM（FP8），把拷贝和计算重叠，吃新硬件。面试报「减 I/O」比报版本号百分比更稳。

FlashDecoding：逐 token 生成（decode） 步 $Q$ 很短（常为 1 个 token），按 KV 长度分块并行算局部 attention 再合并，而不是让单个短 $Q$ 串行扫整条 cache。这是 decode 特化，和 输入预填充（prefill，即处理输入并建立缓存） 的 FA 主路径不同。GQA / MQA 减少 KV head，和 FA 正交：FA 减注意力 I/O 形状，GQA 减 KV 体积。

## Dynamic Batching 在调度什么

静态 batch：组好 $B$ 条，跑到最短的结束仍要陪最长的。continuous batching：每个 decode step 调度当前仍存活的序列，新请求 prefill 完插入，结束的让出 KV 页。通常和 PagedAttention 一起才有吞吐，页式 KV 让不同长度不靠 padding 对齐。它解决的是「长短不一导致算力空转」，没有 policy stale；不要和异步 强化学习（RL） 混。高 QPS 网关还要 admission：KV 池满了先拒，而不是无限插入把 p99 打爆。和 FA 的关系：FA 让每一步的 attention 更便宜；continuous batching 让 GPU 每一步都有足够的活请求。缺调度时 FA 再快也会空等最长序列。

## 面试怎么画

先画 HBM 上 $N\times N$ 被 SRAM 分块替代，再写 online softmax 的 $m,\ell$ 归并。然后画一条时间线：请求 A 还在 decode，请求 B 插入，C 结束释放页。CUDA 追问：block tile 放 shared memory，warp shuffle 做行内 reduce，避免把 softmax 写回 HBM。Serving 追问：vLLM/SGLang 的 scheduler、page table、prefix cache。不要背「V3 快 1.5×」而不说硬件假设。

## 追问

- **为什么必须 online softmax？** 分块后看不到整行。用运行中的行 max $m$ 和归一化项 $\ell$ 在块间 rescale，才能在 SRAM 里得到与物化 $N\times N$ 等价的 softmax。这是 V1 的核心，V2/V3 没换掉它。
- **V2 相对 V1 改了什么？** 序列维更并行、更少 kernel launch、warp 负载更匀，训练吞吐抬头。算法仍是 tiling + online softmax。V3 再吃 Hopper 异步拷贝与低精度 GEMM。
- **FlashDecoding 和 FA 是一回事吗？** 同族，decode 特化：一步的 $Q$ 很短，按 KV 分块并行再合并，避免短 $Q$ 串行扫长 cache。和 GQA 正交，GQA 减的是 KV 体积。
- **Dynamic Batching 是把 batch 加大吗？** 不是。是每个 decode step 插入新请求、踢出已结束序列，避免静态 batch 必须等待最长序列。常与 continuous batching 同指。
- **没有 PagedAttention 行不行？** 调度仍能做，但 KV 靠 padding 或碎片，吞吐上不去。页式分配才让不同长度高效共存。高 QPS 还要 admission，池满先拒而不是无限插入。
