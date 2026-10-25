---
id: xai-moe-decode
section: xai
order: 12
level: S
title: xAI：MoE decode 专家不齐和 batch 碎片
quick: "MoE decode 每序列每步只有一个 token，路由后各专家得到长短不齐的小 GEMM，热点专家和慢链路决定一步耗时。我会根据并发与上下文选择 EP 宽度，使用变长核、grouped GEMM 或热专家复制，并核对 CUDA Graph padding 是否抵消了稀疏收益。"
tags:
  - xAI
  - MoE
  - Decode
  - Serving
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Open Release of Grok-1
    url: https://x.ai/news/grok-os
    type: primary
  - title: Mixtral of Experts
    url: https://arxiv.org/abs/2401.04088
    type: primary
  - title: Switch Transformers
    url: https://arxiv.org/abs/2101.03961
    type: primary
  - title: DeepSeek-V3 Technical Report
    url: https://arxiv.org/abs/2412.19437
    type: secondary
---

MoE decode 容易慢在不均匀的小 GEMM 和通信同步上，需要根据实际 batch 选择并行度与 kernel。例如 Grok-1 公开是 8 专家、$k=2$，$B=32$ 时平均每专家只有 8 个 token，实际还会冷热不均。后续线上架构没有开源，这里用 Mixtral、Switch 和公开 MoE serving 解释机制；路由与 EP 见 `xai-grok-moe`，入口并发见 `xai-rate-limiter`。

## 为什么平均负载看不出尾延迟

Decode 的隐状态是 `[B, 1, d]`。Router 给每个 token top-$k$ 专家。期望每个专家 $Bk/E$ 个 token。Grok-1 数字感：$E=8$、$k=2$，期望 $B/4$。$B=32$ 时期望 8；泊松波动下可能一张卡 20、隔壁 0。Gather 之后专家 $i$ 的输入不是 `[B, d]`，而是 `[n_i, d]`，$n_i$ 每步都变，这就是碎片。

空专家的 $n_i=0$ 仍要在 all-to-all 里占一个槽；热专家的 $n_i$ 决定这一步实际耗时。平均利用率好看，尾延迟由最热那个专家决定。

EP 下每层两次 all-to-all。同步点在最慢专家的计算 + 最慢那条链路。空专家也要参加集合通信，不然 communicator 对不齐。64 层就是每步上百次这种同步。训练可用 aux loss 拉齐 $f_i$；推理没有反向，只能放置（热/冷绑一张卡、复制热专家）或容量溢出时 drop / 改路由。Drop 改质量，复制改显存。Capacity $C=\gamma\cdot Bk/E$，decode 的 $Bk/E$ 经常小于 1，再设 $\gamma$ 也填不满 Tensor Core tile。

因此不能单凭稀疏 FLOPs 推断 decode 更快，还要看路由同步和权重带宽。Grok-1 官方 JAX 示例为了正确性会扫未选专家，生产若照抄，稀疏的好处当场没有。

## 连续 batch 后怎么减少碎片

连续 batching 把不同长度、不同 decode 步的请求拼成一个 `B`。对 dense 注意力，这是 PagedAttention 的日常，见系统卡 `sys-paged-attn`、`sys-cont-batch`。对 MoE，碎片在专家维又加一刀：

同一 decode 步里，$B$ 个 token 被路由打散。专家 $i$ 收到的是下标不连续的一小撮 token，不是整齐的 `[B, d]`。再叠 EP，每张卡上的局部 batch 更小。结果是一堆 grouped GEMM：shape 每步都变。CUDA Graph 要静态 shape，只能按专家上限 padding。一 pad，冷专家也做满 tile，稀疏节省被 padding FLOPs 吃回去。

Prefill 相反：一条请求就有 $T$ 个 token，$T$ 上千时专家容易填满，all-to-all 走带宽。所以 输入预填充（prefill，即处理输入并建立缓存） 可以宽 EP；decode 要短往返，EP 太宽只是多等网。我会主动说分离：两套并行度，KV 搬过去。没有足够并发，decode 侧 MoE 的理论 FLOPs 优势不存在。限流决定 $B$ 的下限，见 `xai-rate-limiter`。

工程对策只讲公开做过的类型，不编 xAI 实现：

1. Grouped GEMM / 变长专家 kernel，少 pad。没有亲自实现过，就明确说明是在讨论公开设计。
2. 热专家复制，把 decode 热点摊开；复制太多 EP 又变 dense。
3. 不要为了 CUDA Graph 按最热专家的历史峰值给所有专家 pad——那是把 MoE 当成 8 路 dense。
4. 统计窗口上的专家占用，而不是一步一迁路由。采样会让专家选择抖，greedy 同一前缀应对齐。

和 dense decode 对比：dense 一步一次大 GEMM，batch 不齐最多是序列 pad；MoE 一步是路由 + 两次 all-to-all + 一堆小 GEMM，batch 不齐变成专家之间的空等。在 314B 这类参数规模下，解释各专家的 shape 和等待关系，才能说明实际开销。

## 追问

**为什么 prefill 看起来利用率更高？**
每条序列贡献 $T$ 个 token 给专家，GEMM 有体积。Decode 每序列贡献 1 个，$B$ 不够就全是启动开销。

**Drop token 行不行？**
训练有时用 capacity drop。Decode 丢隐状态就是改输出分布，用户看得见。宁可延迟或复制专家，不要静默 drop。

**和 Tensor Parallel 叠？**
TP 切同一块矩阵，负载齐；EP 切不同专家，负载不齐。8 专家 $k=2$ 可以 EP 叠 TP，先画通信再叠。Grok-1 单卡放不下全部专家权重，纯「8 专家都本地」在 314B 量级不成立。

**连续 batch 会不会让专家更齐？**
$B$ 大时期望更齐，但请求 mix（短回复 vs 长推理）会让热专家随产品功能变。Think 模式更长 decode，碎片窗口更长，见 `xai-grok-pretrain` 里 Grok-3 的 test-time compute 口径——那是延迟故事，不是许可你编他们的 EP 拓扑。

## 相关题

- [[xai-grok-moe]]：本题的前篇，和本题部分重合，讲 Grok-1 公开配置、EP 的集合通信，以及 prefill/decode 用不同 EP 宽度。
- [[meta-llama-moe]]：Llama 4 服务侧同样遇到小 batch decode 时 all-to-all 比 GEMM 慢。
- [[sys-ep-dispatch]]：从通信角度看同一个问题，一步耗时由收 token 最多的卡决定，以及 decode 专用低延迟核。
- [[nvidia-fused-moe]]：专家小 GEMM 落到 kernel 上的样子，pad 到 `BLOCK_M` 在 decode 上浪费多少。

本卡依据公开材料整理，标记为 `realInterview: false`。
