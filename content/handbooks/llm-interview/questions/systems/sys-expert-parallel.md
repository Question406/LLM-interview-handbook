---
id: sys-expert-parallel
section: systems
order: 33
level: S
title: Expert Parallel（EP）如何切分 MoE？与 TP/DP 组合时通信模式是什么？
quick: "EP 把专家分到不同卡，每张卡只存一部分 expert，再按 router 的结果把 token 发到对应卡计算、把结果送回来。前向经过 router、all-to-all dispatch、本地 GEMM 和 all-to-all combine。TP 可以继续切单个专家的矩阵，DP 再归约同一专家分片的梯度；主要瓶颈常是变长通信和热点卡拖尾。"
tags:
  - MoE
  - Expert Parallel
  - Systems
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: DeepSeek-V3 Technical Report
    url: https://arxiv.org/abs/2412.19437
    type: primary
  - title: Switch Transformers
    url: https://arxiv.org/abs/2101.03961
    type: primary
---

EP 切的是专家集合：每张卡只保存 $N/\mathrm{EP}$ 个 expert，token 由 router 决定发到哪张卡。比如一个 token 选中的专家在别的卡上，就要先传 hidden state，算完再传回结果。Dense FFN 的 TP 切同一套 $W$ 的行或列，每层做 all-reduce；MoE 的专家数 $N$ 可以远大于卡数，把每个专家复制到所有卡会吃掉很多显存。

## 一次前向怎样跨卡

1. 每卡本地 router 算出 top-$k$ 目的 expert。
2. **Dispatch all-to-all**：按目的 rank 把 token hidden 发出去。消息长度随负载变，不是固定 $B\times T$。
3. 本地 expert GEMM（可再套 TP：expert 内部切矩阵）。
4. **Combine all-to-all**：把输出送回 token 原来的 rank，按门控权重加权。

通信量粗算：每个 token 激活 $k$ 个 expert，hidden 维 $d$，每边一次 dispatch/combine，约 $2k\cdot T\cdot d$ 字节量级，还要加变长索引。负载不均时热点卡既算得多、收的也多，拖尾比均值更致命。

DP、TP 和 EP 可以组合，但各自通信的对象不同。

**DP**：不同数据副本各自路由。同一 expert 会汇总来自多个 DP rank 的 token，EP 组内 all-to-all 先发生，梯度再在 DP 上对 **同一 expert 分片**
做 reduce。
- **TP**：切的是单个 expert 的矩阵，通信是 expert 内 collective，模式规则、适合 NVLink 域。
- **EP**：切的是 expert 集合，通信是 token 级不规则 all-to-all。

常见拓扑：节点内 TP $\times$ EP，跨节点 DP。EP size 加大能放下更多 expert，但 all-to-all 跳数和消息碎片变多；当专家计算已经很碎、通信占比 $\gt 50\%$，再加 EP 吞吐会掉。DeepSeek-V3 用 DeepEP 一类专用 kernel 做 dispatch/combine 与计算重叠。面试讲清「不规则 all-to-all + overlap」即可，不必背产品名。

## 追问

**和 `sys-parallel` 那句「EP 切 experts」差在哪？**
那题是五维对照；本题要能画 dispatch/combine，并说清变长消息和热点拖尾。
**EP=专家数时每卡一个 expert？**
可以，但 $k\gt 1$ 时 combine 仍要跨卡；过细的 EP 让 GEMM 太小，算力喂不饱。
**评测看什么？**
tokens/s、all-to-all 占比、每 expert 的 token 直方图、P99 步时。只报 MFU 会掩盖通信。
