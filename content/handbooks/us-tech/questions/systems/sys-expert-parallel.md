---
id: sys-expert-parallel
section: systems
order: 10
level: S
title: 系统：专家并行，token 调度不均和 all-to-all
quick: "专家并行让每张卡只保存一部分 expert，路由后先 all-to-all 发送 token，本地计算，再把输出送回原 rank 加权。它节省专家权重的单卡驻留，但动态通信和热点专家会拖慢整步。调容量、aux loss 和偏置时，要同时看质量与负载尾部。"
tags:
  - Google
  - NVIDIA
  - MoE
  - Expert Parallel
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Switch Transformers — Scaling to Trillion Parameter Models with Simple and Efficient Sparsity
    url: https://arxiv.org/abs/2101.03961
    type: primary
  - title: GShard — Scaling Giant Models with Conditional Computation and Automatic Sharding
    url: https://arxiv.org/abs/2006.16668
    type: primary
  - title: DeepSeek-V3 Technical Report
    url: https://arxiv.org/abs/2412.19437
    type: primary
  - title: Mixtral of Experts
    url: https://arxiv.org/abs/2401.04088
    type: primary
---

EP 按专家集合切卡，每张卡只保存一部分 expert，token 按路由结果发送过去计算，再送回原来的 rank。比如大部分 token 都选中同一卡上的专家，那张卡会同时承担更多通信和计算，其他卡也得等它。这是 Switch / GShard、Megatron-MoE、Mixtral 和 DeepSeek EP 都会面对的问题；与 dense 三维并行的区别见 `sys-3d-parallel`，Google 侧机制见 `google-gemini-moe`。

Dense FFN 用 TP 把同一套 $W$ 按列/行切开，每层一次 all-reduce。MoE 有 $E$ 个 expert，$E$ 可以远大于卡数。还用 TP 把每个 expert 复制到所有卡，显存吃不下。EP 的定义：**每张卡只存 $E/\mathrm{EP}$ 个 expert**，token 按路由结果搬家。

一步前向：

1. 本卡 router 算出 top-$k$ 目的 expert。
2. Dispatch all-to-all：按目的 rank 把 hidden 发出去。消息长度随负载变，不是固定 $B\cdot T$。
3. 本地 expert GEMM（内部还可以再套 TP）。
4. Combine all-to-all：输出送回 token 原来的 rank，按门控权重加权。

通信量粗算 $2k\cdot T\cdot d$ 字节量级（dispatch + combine），外加变长索引。均值好看，尾部由 **收 token 最多的那张卡** 决定：它既算得多，all-to-all 也更堵。这和 dense all-reduce「每卡同样大的固定消息」完全不同。

Router 塌缩时，少数 expert 吃掉大部分 token。Switch 用容量因子：每个 expert 只收 $C\cdot T/E$ 个 token，超出的 drop 或溢出到 backup。容量太小，质量掉；太大，热点卡照样拖尾。Auxiliary load-balancing 损失（loss）、DeepSeek 的 bias 修正、专家 dropout，目的都是让直方图平一点，让 all-to-all 可预测。这些措施既影响训练负载，也能减少通信 P99。

和 DP / TP 叠：

- DP：不同数据副本各自路由，同一 expert 汇总来自多个 DP rank 的 token。
- TP：切单个 expert 内部矩阵，通信规则、适合 NVLink。
- EP：切专家集合，通信是不规则 all-to-all。

常见拓扑：节点内 TP 乘 EP，跨节点 DP。EP 加大能放下更多 expert，但消息更碎、跳数更多；专家计算已经很小、通信占比过半时，再加 EP 吞吐会掉。DeepSeek-V3 用专用 dispatch/combine 和计算重叠；不规则 all-to-all 和 GEMM 同微批有数据依赖，overlap 要切微批。同批 dispatch 与该批 GEMM 有先后依赖，重叠要跨微批安排。

推理侧 输入预填充（prefill，即处理输入并建立缓存） 的 $T$ 大，all-to-all 有体积；逐 token 生成（decode） 每步 token 少，all-to-all 变成小消息延迟墙。所以 MoE serving 经常 prefill / decode 用不同 EP 度，或 decode 把 expert 复制一份换通信。不要把训练拓扑原样搬到 decode。

监控：tokens/s、all-to-all 等待、每 expert 的 token 直方图、P99 步时。只报平均 MFU 会掩盖热点卡在等。

## 追问

**EP 等于专家数、每卡一个 expert 好吗？**
可以，但 $k>1$ 时 combine 仍跨卡；过细的 EP 让 GEMM 太小，算力喂不饱。

**和 TP 的 all-reduce 差在哪？**
TP 尺寸固定、对端固定；EP all-to-all 变长、目的 rank 随 router 变。尾部由热点 expert 决定。

**Token drop 为什么伤 overlap？**
每步 shape 变，静态 CUDA graph 失效；部分 token 走 skip，计算更不齐。

**为什么训练和推理路由不能各搞一套？**
训练看到的 expert 负载和推理不一致，质量会漂。Serving 可以改并行度，不该偷偷改 router。

## 相关题

- [[sys-ep-dispatch]]：本题的续篇，和本题部分重合，把镜头推到 dispatch 这一跳的负载直方图、EPLB 和 decode 低延迟核。
- [[google-gemini-moe]]：Google 版的产品直觉题，路由、容量和 decode 为什么不会便宜 $E$ 倍。
- [[meta-llama-moe]]：Llama 4 服务侧的 EP 和 batch，公开架构下专家权重全驻留、小 batch 时 all-to-all 比 GEMM 慢。
- [[nvidia-moe-gemm]]：EP all-to-all 之后本地那一步怎么算，permute 加一次 grouped GEMM。
