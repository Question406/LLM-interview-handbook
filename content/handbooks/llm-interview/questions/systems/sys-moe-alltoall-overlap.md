---
id: sys-moe-alltoall-overlap
section: systems
order: 270
level: A
title: MoE 的 All-to-All 如何与 GEMM 重叠？什么会挡住 overlap？
quick: >-
  MoE 通信与 GEMM 的重叠要错开微批：当前批算专家 GEMM，下一批做 dispatch，或上一批做 combine。同一微批的 GEMM 要等
  dispatch 的输入，所以直接开双流叠不上。DeepSeek-V3 用 DeepEP 和 DualPipe 组织这类流水，但热点专家、小消息和动态
  shape 仍会把等待暴露出来。
tags:
  - MoE
  - Communication Overlap
  - All-to-All
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DeepSeek-V3 Technical Report
    url: 'https://arxiv.org/abs/2412.19437'
    type: primary
---

## 可以这样回答

MoE 的 all-to-all 要通过错开微批与 GEMM 重叠。同一批 token 必须先 dispatch 到专家所在卡，GEMM 才有输入；能并行的是下一批的通信和当前批的计算。比如 compute stream 处理当前专家输入时，comm stream 提前搬下一批，这才形成独立工作。EP 路由后才知道消息长度，和固定尺寸的 Dense TP all-reduce 不同，机制见 `sys-expert-parallel`；DeepSeek-V3 用 DeepEP 和 DualPipe 把这条流水接起来。

DeepEP 把跨节点 RDMA 与节点内 NVLink 的不规则 all-to-all 做成可与 GEMM 并发的原语，避免「一个 fused kernel 里又算又等」。反向对称：expert 的 dgrad / wgrad 与 combine 梯度的 all-to-all 同样按微批错开。Pipeline 更深时，DualPipe 把前向通信与反向计算叠在相邻 stage，那是 PP 级 overlap，和 EP 微批 overlap 是两层，我会分开说。

## 技术备查

MoE 的 all-to-all 要通过错开微批与 GEMM 重叠。同一批 token 必须先 dispatch 到专家所在卡，GEMM 才有输入；能并行的是下一批的通信和当前批的计算。比如 compute stream 处理当前专家输入时，comm stream 提前搬下一批，这才形成独立工作。EP 路由后才知道消息长度，和固定尺寸的 Dense TP all-reduce 不同，机制见 `sys-expert-parallel`；DeepSeek-V3 用 DeepEP 和 DualPipe 把这条流水接起来。

## 把相邻微批排成流水线

一步前向仍是 router $\to$ dispatch $\to$ 本地 expert GEMM $\to$ combine。通信量粗算 $2k\cdot T\cdot d$ 字节量级，但每 rank 真实收发随负载变。能重叠的调度是：

1. 把 token 切成微批 $m_0,m_1,\ldots$
2. Compute stream 做 $m_i$ 的 expert GEMM；comm stream 同时做 $m_{i+1}$ 的 dispatch（或 $m_{i-1}$ 的 combine）
3. 用 event 同步「GEMM 读的那块 buffer 已经 combine/dispatch 完成」

DeepEP 把跨节点 RDMA 与节点内 NVLink 的不规则 all-to-all 做成可与 GEMM 并发的原语，避免「一个 fused kernel 里又算又等」。反向对称：expert 的 dgrad / wgrad 与 combine 梯度的 all-to-all 同样按微批错开。Pipeline 更深时，DualPipe 把前向通信与反向计算叠在相邻 stage，那是 PP 级 overlap，和 EP 微批 overlap 是两层，我会分开说。

节点内路由限制（token 尽量留在本机）能缩短跨机消息，让 NVLink 上的 overlap 更容易藏住；跨机 hop 一多，即使 kernel 支持 overlap，尾部延迟仍会露出。NVLink 域内带宽高、延迟低，overlap 窗口可以较短；跨节点 RDMA 握手和尾包更贵，微批必须够大才能把这段藏进 GEMM。DeepSeek-V3 把节点受限路由和 DeepEP 一起用，先减少「藏不住的跨机量」，再谈双流。评测看 all-to-all wait time、SM 利用率、每 expert token 直方图，不要只报平均带宽。平均带宽高也可能在等最慢 rank。反向路径同样要排程：combine 梯度没到，wgrad GEMM 就没有完整 token 集合，不能只 overlap 前向却把反向当成免费。

## 哪些等待仍会露出来

**负载不均。**
热点 expert 所在 rank 既算得多、收的也多，barrier 由最慢 expert 决定。Overlap 只能藏平均通信，藏不住 P99。先均衡（aux / bias）或设 capacity，见 `sys-moe-capacity-token-drop`。Capacity 过小则 drop，shape 每步变，图更难叠。
**同批依赖。**
不切微批，dispatch 结束才能 GEMM，通信百分百暴露。微批太碎则 GEMM 变小、启动开销吃掉收益。
**小消息启动开销。**
Hidden 小、$T$ 小或 EP 过细时，launch + 握手比拷贝还贵，overlap 没有可藏的 bulk transfer。
**动态 shape / CUDA graph。**
Token drop、变长 dispatch 让每次 all-to-all 的 count 不同，静态 graph 捕获失败或频繁 re-capture。这是 MoE 比 Dense 更难 overlap 的根因之一。
**隐式同步。**
默认流上随手 `torch.cuda.synchronize`、或把通信输出立刻用在默认流，会把双流打回串行。必须显式 stream 与 buffer 轮换，避免 GEMM 写到通信还在读的那块。

我会先检查路由是否均衡，再选能覆盖通信延迟的微批大小，最后接 DeepEP 这类通信库。热点 expert 的等待还要靠均衡和容量处理，多开 stream 也不会减少它必须完成的工作量。

## 追问

**为什么同批 dispatch 不能和该批 GEMM 重叠？**
GEMM 的输入就是 dispatch 的输出。没有切微批就没有独立的生产者-消费者对。
**和 Dense all-reduce overlap 差在哪？**
Dense 尺寸固定、对端固定；MoE all-to-all 变长、目的 rank 随 router 变。尾部由热点 expert 决定。
**Capacity / drop 如何破坏 overlap？**
每步 shape 变，缓冲与 graph 失效；drop 还让部分 token 走 skip，计算量更不齐。
**微批是不是越小越好？**
不是。太小 GEMM 喂不饱 Tensor Core，启动开销大于隐藏的通信。要能覆盖一次 all-to-all 延迟的最小计算块。
**监控为什么不能只看总线带宽？**
带宽均值可以很好，GPU 仍在等最慢 expert。看 wait time、token 直方图和 SM 空闲。
---
